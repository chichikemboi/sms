from django.contrib import admin
from .models import Period, TimetableSlot


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'is_break', 'order']
    ordering = ['order']


@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ['class_section', 'get_day_display', 'period', 'subject', 'teacher', 'room']
    list_filter = ['day', 'class_section__stream']
