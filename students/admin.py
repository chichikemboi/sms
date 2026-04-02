from django.contrib import admin
from .models import Student, Guardian, ClassSection, Stream


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'order']
    ordering = ['order']


@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'stream', 'section', 'class_teacher']
    list_filter = ['stream']


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'relation', 'phone_primary', 'email']
    search_fields = ['first_name', 'last_name', 'phone_primary']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'full_name', 'class_section', 'boarding_type', 'status']
    list_filter = ['class_section__stream', 'status', 'boarding_type']
    search_fields = ['first_name', 'last_name', 'admission_number', 'nemis_no']
    ordering = ['class_section', 'last_name']
