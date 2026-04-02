from django.db import models
from students.models import ClassSection
from exams.models import Subject


class SyllabusUnit(models.Model):
    """A topic/unit from the official syllabus."""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='units')
    stream = models.ForeignKey(
        'students.Stream', on_delete=models.CASCADE, related_name='units',
        help_text='Which form/grade this unit applies to'
    )
    title = models.CharField(max_length=120)
    objectives = models.TextField(blank=True, help_text='Learning objectives for this unit')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['subject', 'order']

    def __str__(self):
        return f'{self.subject.name} — {self.title}'


class LessonPlan(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_SUBMITTED = 'submitted'
    STATUS_APPROVED = 'approved'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_APPROVED, 'Approved'),
    ]

    teacher = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='lesson_plans',
        limit_choices_to={'role__in': ['subject_teacher', 'class_teacher', 'admin']},
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lesson_plans')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='lesson_plans')
    unit = models.ForeignKey(SyllabusUnit, on_delete=models.SET_NULL, null=True, blank=True)
    week_number = models.PositiveSmallIntegerField(help_text='Week of term (1–14)')
    term = models.PositiveSmallIntegerField(choices=[(1,'Term 1'),(2,'Term 2'),(3,'Term 3')])
    year = models.PositiveSmallIntegerField()
    topic = models.CharField(max_length=160)
    objectives = models.TextField(help_text='What students will be able to do by end of lesson')
    content_outline = models.TextField(help_text='Key content points to cover')
    teaching_methods = models.CharField(max_length=200, blank=True, help_text='e.g. Discussion, Experiment, Demo')
    resources = models.TextField(blank=True, help_text='Textbooks, lab equipment, charts, etc.')
    assessment = models.TextField(blank=True, help_text='How learning will be assessed')
    remarks = models.TextField(blank=True, help_text='Post-lesson reflections (fill after the lesson)')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-term', 'week_number']

    def __str__(self):
        return f'W{self.week_number} T{self.term}/{self.year} — {self.subject.name}: {self.topic}'


class TopicCoverage(models.Model):
    """Tracks whether a syllabus unit has been covered."""
    unit = models.ForeignKey(SyllabusUnit, on_delete=models.CASCADE, related_name='coverage')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='coverage')
    teacher = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='coverage_records'
    )
    term = models.PositiveSmallIntegerField(choices=[(1,'Term 1'),(2,'Term 2'),(3,'Term 3')])
    year = models.PositiveSmallIntegerField()
    is_covered = models.BooleanField(default=False)
    date_covered = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['unit', 'class_section', 'term', 'year']
        ordering = ['unit__order']

    def __str__(self):
        return f'{self.unit} — {self.class_section}: {"✓" if self.is_covered else "✗"}'
