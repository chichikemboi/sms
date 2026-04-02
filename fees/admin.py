from django.contrib import admin
from .models import FeeStructure, FeePayment, FeeBalance

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['stream', 'term', 'year', 'tuition', 'boarding', 'total']
    list_filter = ['year', 'term', 'stream']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'term', 'year', 'amount', 'method', 'reference', 'date_paid']
    list_filter = ['year', 'term', 'method']
    search_fields = ['student__first_name', 'student__last_name', 'reference']

@admin.register(FeeBalance)
class FeeBalanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'term', 'year', 'expected', 'paid', 'balance']
    list_filter = ['year', 'term']
