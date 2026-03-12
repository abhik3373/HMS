from django.db import models
from django.conf import settings
from doctors.models import AvailabilitySlot


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        limit_choices_to={'role': 'patient'}
    )
    slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.CASCADE,
        related_name='appointment'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    doctor_calendar_event_id = models.CharField(max_length=255, blank=True)
    patient_calendar_event_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.get_full_name()} → Dr.{self.slot.doctor.get_full_name()} on {self.slot.date}"
