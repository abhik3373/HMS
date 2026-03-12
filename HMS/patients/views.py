from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from core.decorators import patient_required
from core.email_service import call_email_service
from core.calendar_helper import trigger_google_calendar
from doctors.models import AvailabilitySlot
from accounts.models import User
from .models import Appointment
import datetime


@login_required
@patient_required
def patient_dashboard(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related('slot', 'slot__doctor').order_by('-slot__date')
    return render(request, 'patients/dashboard.html', {'appointments': appointments})


@login_required
@patient_required
def doctor_list(request):
    doctors = User.objects.filter(role='doctor').order_by('first_name')
    return render(request, 'patients/doctor_list.html', {'doctors': doctors})


@login_required
@patient_required
def slot_list(request, doctor_id):
    doctor = get_object_or_404(User, pk=doctor_id, role='doctor')
    today = datetime.date.today()
    slots = AvailabilitySlot.objects.filter(
        doctor=doctor,
        date__gte=today,
        is_booked=False
    ).order_by('date', 'start_time')
    return render(request, 'patients/slot_list.html', {'doctor': doctor, 'slots': slots})


@login_required
@patient_required
def book_slot(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot, pk=slot_id)

    # Pre-check before showing form
    if slot.is_booked:
        messages.error(request, 'Sorry, this slot was just booked by someone else.')
        return redirect('slot_list', doctor_id=slot.doctor.id)

    if request.method == 'POST':
        try:
            print(f"\n[BOOKING] Starting booking for slot {slot_id}")
            print(f"[BOOKING] Patient: {request.user.username} | Email: {request.user.email}")
            print(f"[BOOKING] Doctor: {slot.doctor.username} | Email: {slot.doctor.email}")

            with transaction.atomic():
                slot = AvailabilitySlot.objects.select_for_update().get(pk=slot_id)
                if slot.is_booked:
                    messages.error(request, 'Sorry, this slot was just booked by someone else.')
                    return redirect('slot_list', doctor_id=slot.doctor.id)

                slot.is_booked = True
                slot.save()
                print(f"[BOOKING] Slot marked as booked ✅")

                appointment = Appointment.objects.create(
                    patient=request.user,
                    slot=slot,
                    status='confirmed'
                )
                print(f"[BOOKING] Appointment created: ID={appointment.pk} ✅")

            print(f"[BOOKING] Triggering calendar (background)...")
            trigger_google_calendar(appointment)

            print(f"[BOOKING] Sending email to patient: {request.user.email}")
            call_email_service(
                action='BOOKING_CONFIRMATION',
                to_email=request.user.email,
                data={
                    'recipient_name': request.user.get_full_name(),
                    'doctor_name': slot.doctor.get_full_name(),
                    'patient_name': request.user.get_full_name(),
                    'date': str(slot.date),
                    'start_time': str(slot.start_time),
                    'end_time': str(slot.end_time),
                }
            )

            print(f"[BOOKING] Sending email to doctor: {slot.doctor.email}")
            call_email_service(
                action='BOOKING_CONFIRMATION',
                to_email=slot.doctor.email,
                data={
                    'recipient_name': f"Dr. {slot.doctor.get_full_name()}",
                    'doctor_name': slot.doctor.get_full_name(),
                    'patient_name': request.user.get_full_name(),
                    'date': str(slot.date),
                    'start_time': str(slot.start_time),
                    'end_time': str(slot.end_time),
                }
            )

            print(f"[BOOKING] All done! Redirecting to success page ✅")
            messages.success(request, '✅ Appointment booked successfully!')
            return redirect('booking_success', pk=appointment.pk)

        except Exception as e:
            print(f"[BOOKING] ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Booking failed: {str(e)}')
            return redirect('slot_list', doctor_id=slot.doctor.id)

    return render(request, 'patients/book_confirm.html', {'slot': slot})


@login_required
@patient_required
def booking_success(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)
    return render(request, 'patients/booking_success.html', {'appointment': appointment})
