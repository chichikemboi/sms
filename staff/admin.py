from django.contrib import admin
from .models import StaffProfile

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'tsc_number', 'employment_status', 'date_joined', 'is_active']
    list_filter = ['employment_status', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'tsc_number']
