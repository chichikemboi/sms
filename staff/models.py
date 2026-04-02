from django.db import models


class StaffProfile(models.Model):
    TSC_STATUS_CHOICES = [
        ('tsc', 'TSC Employed'),
        ('bom', 'BOM Employed'),
        ('intern', 'Teaching Intern'),
        ('support', 'Support Staff'),
    ]

    user = models.OneToOneField(
        'accounts.User', on_delete=models.CASCADE, related_name='staff_profile'
    )
    tsc_number = models.CharField(max_length=30, blank=True, help_text='TSC Registration Number')
    national_id = models.CharField(max_length=20, blank=True)
    employment_status = models.CharField(max_length=20, choices=TSC_STATUS_CHOICES, default='tsc')
    date_joined = models.DateField(null=True, blank=True)
    subjects_taught = models.ManyToManyField('exams.Subject', blank=True, related_name='staff')
    qualification = models.CharField(max_length=120, blank=True, help_text='e.g. B.Ed Science, PGDE')
    specialization = models.CharField(max_length=120, blank=True)
    emergency_contact_name = models.CharField(max_length=80, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=80, blank=True)
    bank_account = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['user__last_name']

    def __str__(self):
        return f'{self.user.get_full_name()} — Staff Profile'
