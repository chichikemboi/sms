from django.db import models
from django.core.validators import RegexValidator


phone_validator = RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')


class Stream(models.Model):
    """e.g. Form 1, Form 2, Form 3, Form 4 (or Grade 10, 11, 12 for CBC)"""
    name = models.CharField(max_length=20, unique=True)  # e.g. 'Form 4'
    label = models.CharField(max_length=40, blank=True)  # e.g. 'Form Four'
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ClassSection(models.Model):
    """e.g. Form 4A, Form 4B"""
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='sections')
    section = models.CharField(max_length=5)  # e.g. 'A', 'B', 'East'
    class_teacher = models.ForeignKey(
        'accounts.User',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='class_sections',
        limit_choices_to={'role__in': ['class_teacher', 'admin']},
    )

    class Meta:
        unique_together = ['stream', 'section']
        ordering = ['stream__order', 'section']

    def __str__(self):
        return f'{self.stream.name}{self.section}'

    @property
    def full_name(self):
        return f'{self.stream.name} {self.section}'


class Guardian(models.Model):
    RELATION_CHOICES = [
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('guardian', 'Guardian'),
        ('sibling', 'Sibling'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('other', 'Other'),
    ]
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, default='guardian')
    phone_primary = models.CharField(max_length=20, validators=[phone_validator])
    phone_secondary = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    id_number = models.CharField(max_length=20, blank=True, help_text='National ID or Passport')
    occupation = models.CharField(max_length=80, blank=True)
    address = models.TextField(blank=True)

    # If guardian is a registered parent user
    user = models.OneToOneField(
        'accounts.User',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='guardian_profile',
        limit_choices_to={'role': 'parent'},
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.get_relation_display()})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Student(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_TRANSFERRED = 'transferred'
    STATUS_COMPLETED = 'completed'
    STATUS_SUSPENDED = 'suspended'
    STATUS_WITHDRAWN = 'withdrawn'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_TRANSFERRED, 'Transferred'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_SUSPENDED, 'Suspended'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    ]

    BOARDING_CHOICES = [
        ('day', 'Day Scholar'),
        ('boarding', 'Boarding'),
    ]

    # Identification
    admission_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=60)
    middle_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('female', 'Female'), ('male', 'Male')], default='female')
    photo = models.ImageField(upload_to='students/photos/', null=True, blank=True)
    kcpe_index = models.CharField(max_length=20, blank=True, help_text='KCPE Index Number')
    kcpe_marks = models.PositiveSmallIntegerField(null=True, blank=True)
    nemis_no = models.CharField(max_length=20, blank=True, help_text='NEMIS UPI Number')

    # Enrollment
    class_section = models.ForeignKey(ClassSection, on_delete=models.PROTECT, related_name='students')
    date_admitted = models.DateField()
    boarding_type = models.CharField(max_length=10, choices=BOARDING_CHOICES, default='day')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    # Guardian
    guardian = models.ForeignKey(Guardian, on_delete=models.PROTECT, related_name='students')

    # Additional
    medical_notes = models.TextField(blank=True)
    special_needs = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text='Internal admin notes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['class_section', 'last_name', 'first_name']

    def __str__(self):
        return f'{self.admission_number} — {self.full_name}'

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(p for p in parts if p)

    @property
    def short_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE
