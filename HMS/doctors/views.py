from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import doctor_required
from .models import AvailabilitySlot
from .forms import AvailabilitySlotForm
import datetime


@login_required
@doctor_required
def doctor_dashboard(request):
    today = datetime.date.today()
    slots = AvailabilitySlot.objects.filter(doctor=request.user).order_by('date', 'start_time')
    upcoming = slots.filter(date__gte=today)
    past = slots.filter(date__lt=today)

    return render(request, 'doctors/dashboard.html', {
        'upcoming_slots': upcoming,
        'past_slots': past,
        'today': today,
    })


@login_required
@doctor_required
def add_slot(request):
    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.doctor = request.user
            # Check for duplicate
            if AvailabilitySlot.objects.filter(
                doctor=request.user,
                date=slot.date,
                start_time=slot.start_time
            ).exists():
                messages.error(request, 'You already have a slot at this date and time.')
            else:
                slot.save()
                messages.success(request, f'Slot added: {slot.date} {slot.start_time}–{slot.end_time}')
                return redirect('doctor_dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = AvailabilitySlotForm()
    return render(request, 'doctors/slot_form.html', {'form': form, 'action': 'Add'})


@login_required
@doctor_required
def edit_slot(request, pk):
    slot = get_object_or_404(AvailabilitySlot, pk=pk, doctor=request.user)
    if slot.is_booked:
        messages.error(request, 'Cannot edit a booked slot.')
        return redirect('doctor_dashboard')

    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slot updated successfully.')
            return redirect('doctor_dashboard')
    else:
        form = AvailabilitySlotForm(instance=slot)
    return render(request, 'doctors/slot_form.html', {'form': form, 'action': 'Edit', 'slot': slot})


@login_required
@doctor_required
def delete_slot(request, pk):
    slot = get_object_or_404(AvailabilitySlot, pk=pk, doctor=request.user)
    if slot.is_booked:
        messages.error(request, 'Cannot delete a booked slot.')
        return redirect('doctor_dashboard')
    if request.method == 'POST':
        slot.delete()
        messages.success(request, 'Slot deleted.')
        return redirect('doctor_dashboard')
    return render(request, 'doctors/delete_confirm.html', {'slot': slot})
