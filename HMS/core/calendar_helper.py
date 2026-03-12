from datetime import datetime
import threading


def _do_calendar(appointment):
    """Internal calendar creation — runs in background thread."""
    try:
        from core.google_auth import get_calendar_service
        slot = appointment.slot
        doctor = slot.doctor
        patient = appointment.patient

        start_dt = datetime.combine(slot.date, slot.start_time)
        end_dt = datetime.combine(slot.date, slot.end_time)
        description = (
            f"HMS Appointment\n"
            f"Doctor: Dr. {doctor.get_full_name()}\n"
            f"Patient: {patient.get_full_name()}"
        )

        needs_save = False

        # Doctor's calendar
        if doctor.google_token:
            try:
                service = get_calendar_service(doctor.google_token)
                event = {
                    'summary': f"Appointment with {patient.get_full_name()}",
                    'description': description,
                    'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
                    'end':   {'dateTime': end_dt.isoformat(),   'timeZone': 'Asia/Kolkata'},
                }
                created = service.events().insert(calendarId='primary', body=event).execute()
                appointment.doctor_calendar_event_id = created.get('id', '')
                needs_save = True
                print(f"[Calendar] ✅ Doctor event created: {appointment.doctor_calendar_event_id}")
            except Exception as e:
                print(f"[Calendar] ⚠️  Doctor calendar error: {e}")

        # Patient's calendar
        if patient.google_token:
            try:
                service = get_calendar_service(patient.google_token)
                event = {
                    'summary': f"Appointment with Dr. {doctor.get_full_name()}",
                    'description': description,
                    'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
                    'end':   {'dateTime': end_dt.isoformat(),   'timeZone': 'Asia/Kolkata'},
                }
                created = service.events().insert(calendarId='primary', body=event).execute()
                appointment.patient_calendar_event_id = created.get('id', '')
                needs_save = True
                print(f"[Calendar] ✅ Patient event created: {appointment.patient_calendar_event_id}")
            except Exception as e:
                print(f"[Calendar] ⚠️  Patient calendar error: {e}")

        if needs_save:
            appointment.save()

    except Exception as e:
        print(f"[Calendar] ⚠️  Unexpected error: {e}")


def trigger_google_calendar(appointment):
    """Fire-and-forget calendar creation in background thread."""
    thread = threading.Thread(target=_do_calendar, args=(appointment,), daemon=True)
    thread.start()
    # Never blocks the main request!
