from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'get_doctor', 'get_date', 'get_time', 'status', 'created_at']
    list_filter = ['status', 'slot__date']
    search_fields = ['patient__username', 'slot__doctor__username']

    def get_doctor(self, obj):
        return obj.slot.doctor.get_full_name()
    get_doctor.short_description = 'Doctor'

    def get_date(self, obj):
        return obj.slot.date
    get_date.short_description = 'Date'

    def get_time(self, obj):
        return f"{obj.slot.start_time}–{obj.slot.end_time}"
    get_time.short_description = 'Time'
