from django import forms
from .models import AvailabilitySlot
import datetime


class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('date')
        start_time = cleaned.get('start_time')
        end_time = cleaned.get('end_time')

        if date and date < datetime.date.today():
            raise forms.ValidationError("Cannot create slots in the past.")

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")

        return cleaned
