from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_ADMIN = 'admin'
    ROLE_CLASS_TEACHER = 'class_teacher'
    ROLE_SUBJECT_TEACHER = 'subject_teacher'
    ROLE_PARENT = 'parent'
    ROLE_BURSAR = 'bursar'
    ROLE_AUDITOR = 'auditor'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin / Headteacher'),
        (ROLE_CLASS_TEACHER, 'Class Teacher'),
        (ROLE_SUBJECT_TEACHER, 'Subject Teacher'),
        (ROLE_PARENT, 'Parent (View Only)'),
        (ROLE_BURSAR, 'Bursar / Accounts'),
        (ROLE_AUDITOR, 'Auditor'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_SUBJECT_TEACHER,
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Teachers: which class they are form/class teacher of (e.g. "Form 4A")
    class_assigned = models.CharField(max_length=20, blank=True, help_text='e.g. Form 4A')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'

    # --- Role helpers ---
    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_class_teacher(self):
        return self.role == self.ROLE_CLASS_TEACHER

    @property
    def is_subject_teacher(self):
        return self.role == self.ROLE_SUBJECT_TEACHER

    @property
    def is_any_teacher(self):
        return self.role in (self.ROLE_CLASS_TEACHER, self.ROLE_SUBJECT_TEACHER)

    @property
    def is_parent(self):
        return self.role == self.ROLE_PARENT

    @property
    def is_bursar(self):
        return self.role == self.ROLE_BURSAR

    @property
    def is_auditor(self):
        return self.role == self.ROLE_AUDITOR

    @property
    def can_edit_fees(self):
        return self.role in (self.ROLE_ADMIN, self.ROLE_BURSAR)

    @property
    def can_view_fees(self):
        return self.role in (self.ROLE_ADMIN, self.ROLE_BURSAR, self.ROLE_AUDITOR, self.ROLE_PARENT)

    @property
    def can_enter_marks(self):
        return self.role in (self.ROLE_ADMIN, self.ROLE_CLASS_TEACHER, self.ROLE_SUBJECT_TEACHER)

    @property
    def dashboard_modules(self):
        """Returns list of module dicts this user can access on the dashboard."""
        all_modules = {
            'students': {
                'name': 'Student Records',
                'icon': 'bi-person-lines-fill',
                'url': '/students/',
                'color': 'primary',
                'desc': 'Admissions, profiles, guardian info',
                'roles': [self.ROLE_ADMIN, self.ROLE_CLASS_TEACHER],
            },
            'exams': {
                'name': 'Marks & Exam Analysis',
                'icon': 'bi-bar-chart-line-fill',
                'url': '/exams/',
                'color': 'success',
                'desc': 'Enter marks, view reports, analysis',
                'roles': [self.ROLE_ADMIN, self.ROLE_CLASS_TEACHER, self.ROLE_SUBJECT_TEACHER],
            },
            'fees': {
                'name': 'Fee Management',
                'icon': 'bi-cash-coin',
                'url': '/fees/',
                'color': 'warning',
                'desc': 'Invoices, payments, balances',
                'roles': [self.ROLE_ADMIN, self.ROLE_BURSAR, self.ROLE_AUDITOR, self.ROLE_PARENT],
            },
            'letters': {
                'name': 'Parent Letters',
                'icon': 'bi-envelope-paper-fill',
                'url': '/letters/',
                'color': 'info',
                'desc': 'Report cards, fee statements, bulk print',
                'roles': [self.ROLE_ADMIN, self.ROLE_CLASS_TEACHER],
            },
            'attendance': {
                'name': 'Attendance',
                'icon': 'bi-calendar2-check-fill',
                'url': '/attendance/',
                'color': 'danger',
                'desc': 'Daily marking, absentee reports',
                'roles': [self.ROLE_ADMIN, self.ROLE_CLASS_TEACHER, self.ROLE_PARENT],
            },
            'staff': {
                'name': 'Staff Management',
                'icon': 'bi-people-fill',
                'url': '/staff/',
                'color': 'secondary',
                'desc': 'Teacher profiles, subjects, records',
                'roles': [self.ROLE_ADMIN],
            },
            'inventory': {
                'name': 'Resource Inventory',
                'icon': 'bi-box-seam-fill',
                'url': '/inventory/',
                'color': 'dark',
                'desc': 'Lab equipment, books, furniture',
                'roles': [self.ROLE_ADMIN],
            },
            'timetable': {
                'name': 'Timetable',
                'icon': 'bi-grid-3x3-gap-fill',
                'url': '/timetable/',
                'color': 'primary',
                'desc': 'Class schedules, room allocation',
                'roles': [self.ROLE_ADMIN, self.ROLE_CLASS_TEACHER, self.ROLE_SUBJECT_TEACHER],
            },
            'lessons': {
                'name': 'Lesson Plans',
                'icon': 'bi-journal-bookmark-fill',
                'url': '/lessons/',
                'color': 'success',
                'desc': 'Weekly plans, syllabus coverage',
                'roles': [self.ROLE_ADMIN, self.ROLE_CLASS_TEACHER, self.ROLE_SUBJECT_TEACHER],
            },
        }

        if self.is_admin:
            return list(all_modules.values())

        return [
            mod for mod in all_modules.values()
            if self.role in mod['roles']
        ]
