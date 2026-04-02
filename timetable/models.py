from django.db import models
from students.models import ClassSection
from exams.models import Subject


class Period(models.Model):
    """Defines the time slots in a school day."""
    name = models.CharField(max_length=20)        # e.g. "Period 1", "Break"
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)  # Break/lunch periods
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.name} ({self.start_time.strftime("%H:%M")}–{self.end_time.strftime("%H:%M")})'


class TimetableSlot(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'),
    ]

    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='timetable_slots')
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='slots')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='timetable_slots',
        limit_choices_to={'role__in': ['subject_teacher', 'class_teacher', 'admin']},
    )
    room = models.CharField(max_length=40, blank=True)

    class Meta:
        unique_together = ['class_section', 'day', 'period']
        ordering = ['class_section', 'day', 'period__order']

    def __str__(self):
        return f'{self.class_section} — {self.get_day_display()} {self.period.name}: {self.subject}'
