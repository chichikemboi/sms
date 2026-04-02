from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import Student, ClassSection, Stream


class Subject(models.Model):
    CURRICULUM_KCSE = 'kcse'
    CURRICULUM_CBC = 'cbc'
    CURRICULUM_CHOICES = [
        (CURRICULUM_KCSE, 'KCSE (8-4-4)'),
        (CURRICULUM_CBC, 'CBC'),
    ]
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=10, unique=True)
    curriculum = models.CharField(max_length=10, choices=CURRICULUM_CHOICES, default=CURRICULUM_KCSE)
    is_compulsory = models.BooleanField(default=True)
    max_score = models.PositiveSmallIntegerField(default=100)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class TeacherSubjectAssignment(models.Model):
    """Links a subject teacher to a subject + class section."""
    teacher = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='subject_assignments',
        limit_choices_to={'role__in': ['subject_teacher', 'class_teacher', 'admin']},
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='subject_assignments')

    class Meta:
        unique_together = ['teacher', 'subject', 'class_section']
        ordering = ['class_section', 'subject']

    def __str__(self):
        return f'{self.teacher.get_full_name()} — {self.subject.name} ({self.class_section})'


class Exam(models.Model):
    TERM_1 = 1
    TERM_2 = 2
    TERM_3 = 3
    TERM_CHOICES = [(1, 'Term 1'), (2, 'Term 2'), (3, 'Term 3')]

    TYPE_OPENER = 'opener'
    TYPE_MID = 'mid'
    TYPE_END = 'end'
    TYPE_MOCK = 'mock'
    TYPE_INTERNAL = 'internal'
    TYPE_CHOICES = [
        (TYPE_OPENER, 'Opener'),
        (TYPE_MID, 'Mid-Term'),
        (TYPE_END, 'End of Term'),
        (TYPE_MOCK, 'Mock / Trial'),
        (TYPE_INTERNAL, 'Internal Assessment'),
    ]

    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_END)
    term = models.PositiveSmallIntegerField(choices=TERM_CHOICES)
    year = models.PositiveSmallIntegerField()
    streams = models.ManyToManyField(Stream, related_name='exams', blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False, help_text='Visible to parents when published')
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='exams_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-term', 'name']

    def __str__(self):
        return f'{self.name} — {self.get_term_display()} {self.year}'


# ── KCSE Grading ──────────────────────────────────────────────────────────────

KCSE_GRADES = [
    (80, 'A',  12),
    (75, 'A-', 11),
    (70, 'B+', 10),
    (65, 'B',   9),
    (60, 'B-',  8),
    (55, 'C+',  7),
    (50, 'C',   6),
    (45, 'C-',  5),
    (40, 'D+',  4),
    (35, 'D',   3),
    (30, 'D-',  2),
    ( 0, 'E',   1),
]

CBC_GRADES = [
    (85, 'EE', 'Exceeding Expectation'),
    (70, 'ME', 'Meeting Expectation'),
    (50, 'AE', 'Approaching Expectation'),
    ( 0, 'BE', 'Below Expectation'),
]


def get_kcse_grade(score):
    if score is None:
        return None, None
    for threshold, grade, points in KCSE_GRADES:
        if score >= threshold:
            return grade, points
    return 'E', 1


def get_cbc_grade(score):
    if score is None:
        return None, None
    for threshold, grade, label in CBC_GRADES:
        if score >= threshold:
            return grade, label
    return 'BE', 'Below Expectation'


class Mark(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    score = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    is_absent = models.BooleanField(default=False)
    comment = models.CharField(max_length=120, blank=True)
    entered_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='marks_entered'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['exam', 'student', 'subject']
        ordering = ['student__last_name', 'subject__order']

    def __str__(self):
        return f'{self.student.short_name} — {self.subject.name}: {self.score}'

    @property
    def grade(self):
        if self.is_absent:
            return 'ABS'
        grade, _ = get_kcse_grade(float(self.score) if self.score is not None else None)
        return grade

    @property
    def points(self):
        if self.is_absent or self.score is None:
            return 0
        _, pts = get_kcse_grade(float(self.score))
        return pts
