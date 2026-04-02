from django.db import models


class InventoryCategory(models.Model):
    name = models.CharField(max_length=60, unique=True)
    icon = models.CharField(max_length=40, default='bi-box-seam')

    class Meta:
        verbose_name_plural = 'Inventory Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    CONDITION_CHOICES = [
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor / Damaged'),
        ('lost', 'Lost'),
    ]

    category = models.ForeignKey(InventoryCategory, on_delete=models.SET_NULL, null=True, related_name='items')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good')
    location = models.CharField(max_length=80, blank=True, help_text='e.g. Science Lab, Library')
    serial_number = models.CharField(max_length=60, blank=True)
    date_acquired = models.DateField(null=True, blank=True)
    value_kes = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                    help_text='Approximate value in KSh')
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return f'{self.name} ({self.quantity})'
