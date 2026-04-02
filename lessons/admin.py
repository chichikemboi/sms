from django.contrib import admin
from .models import SyllabusUnit, LessonPlan, TopicCoverage


@admin.register(SyllabusUnit)
class SyllabusUnitAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'stream', 'order']
    list_filter = ['subject', 'stream']
    ordering = ['subject', 'order']


@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ['topic', 'subject', 'class_section', 'week_number', 'term', 'year', 'status', 'teacher']
    list_filter = ['term', 'year', 'status', 'subject']
    search_fields = ['topic', 'teacher__first_name', 'teacher__last_name']


@admin.register(TopicCoverage)
class TopicCoverageAdmin(admin.ModelAdmin):
    list_display = ['unit', 'class_section', 'term', 'year', 'is_covered', 'date_covered']
    list_filter = ['is_covered', 'term', 'year']
