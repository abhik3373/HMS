from django.contrib import admin
from .models import AvailabilitySlot


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'start_time', 'end_time', 'is_booked']
    list_filter = ['is_booked', 'date']
    search_fields = ['doctor__username', 'doctor__first_name']
