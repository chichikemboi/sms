from django.contrib import admin
from .models import Subject, Exam, Mark, TeacherSubjectAssignment


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'curriculum', 'is_compulsory', 'max_score', 'order']
    list_filter = ['curriculum', 'is_compulsory']
    ordering = ['order', 'name']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'term', 'year', 'is_published']
    list_filter = ['term', 'year', 'exam_type', 'is_published']


@admin.register(TeacherSubjectAssignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'class_section']
    list_filter = ['subject', 'class_section__stream']


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'subject', 'score', 'is_absent']
    list_filter = ['exam', 'subject', 'is_absent']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']
