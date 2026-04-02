from django.db import models
from students.models import Student, ClassSection


class AttendanceRecord(models.Model):
    STATUS_PRESENT = 'P'
    STATUS_ABSENT = 'A'
    STATUS_LATE = 'L'
    STATUS_EXCUSED = 'E'
    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
        (STATUS_LATE, 'Late'),
        (STATUS_EXCUSED, 'Excused'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    notes = models.CharField(max_length=200, blank=True)
    marked_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='attendance_marked'
    )

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', 'student__last_name']

    def __str__(self):
        return f'{self.student.short_name} — {self.date}: {self.status}'
