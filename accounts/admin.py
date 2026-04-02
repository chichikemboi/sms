from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'get_full_name', 'role', 'class_assigned', 'phone', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone']
    ordering = ['role', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Boenix SMS', {
            'fields': ('role', 'phone', 'class_assigned', 'profile_photo'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Boenix SMS', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'phone', 'class_assigned'),
        }),
    )
