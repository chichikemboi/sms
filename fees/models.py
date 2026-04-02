from django.db import models
from students.models import Student, Stream


class FeeStructure(models.Model):
    """Defines the expected fee per term per stream."""
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='fee_structures')
    term = models.PositiveSmallIntegerField(choices=[(1,'Term 1'),(2,'Term 2'),(3,'Term 3')])
    year = models.PositiveSmallIntegerField()
    tuition = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    boarding = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['stream', 'term', 'year']
        ordering = ['-year', '-term']

    def __str__(self):
        return f'{self.stream} — Term {self.term} {self.year}'

    @property
    def total(self):
        return self.tuition + self.boarding + self.activity + self.other


class FeePayment(models.Model):
    METHOD_MPESA = 'mpesa'
    METHOD_BANK = 'bank'
    METHOD_CASH = 'cash'
    METHOD_CHOICES = [
        (METHOD_MPESA, 'M-Pesa'),
        (METHOD_BANK, 'Bank Transfer'),
        (METHOD_CASH, 'Cash'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    term = models.PositiveSmallIntegerField(choices=[(1,'Term 1'),(2,'Term 2'),(3,'Term 3')])
    year = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default=METHOD_MPESA)
    reference = models.CharField(max_length=60, blank=True, help_text='M-Pesa code, bank ref, receipt no.')
    date_paid = models.DateField()
    received_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='payments_received'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_paid', '-created_at']

    def __str__(self):
        return f'{self.student.short_name} — KSh {self.amount} ({self.date_paid})'


class FeeBalance(models.Model):
    """Computed balance per student per term (updated on payment save)."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='balances')
    term = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    expected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ['student', 'term', 'year']
        ordering = ['-year', '-term']

    @property
    def balance(self):
        return self.expected - self.paid

    @property
    def is_cleared(self):
        return self.balance <= 0

    def __str__(self):
        return f'{self.student.short_name} T{self.term}/{self.year}: {self.balance}'
