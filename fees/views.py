from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django import forms as django_forms
from datetime import date

from accounts.decorators import role_required
from students.models import Student
from .models import FeePayment, FeeBalance, FeeStructure


class PaymentForm(django_forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['student', 'term', 'year', 'amount', 'method', 'reference', 'date_paid', 'notes']
        widgets = {
            'date_paid': django_forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': django_forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, django_forms.Select):
                w.attrs.setdefault('class', 'form-select')
            elif not isinstance(w, (django_forms.DateInput, django_forms.Textarea)):
                w.attrs.setdefault('class', 'form-control')
        self.fields['student'].queryset = (
            Student.objects.filter(status='active').order_by('class_section', 'last_name')
        )
        if not self.initial.get('date_paid') and not self.data.get('date_paid'):
            self.initial['date_paid'] = date.today().isoformat()


@login_required
@role_required('admin', 'bursar', 'auditor', 'parent')
def fee_dashboard(request):
    year = int(request.GET.get('year', date.today().year))
    term = int(request.GET.get('term', 1))

    balances = FeeBalance.objects.filter(year=year, term=term).select_related(
        'student__class_section__stream'
    ).order_by('student__class_section', 'student__last_name')

    # Filter
    q = request.GET.get('q', '')
    if q:
        balances = balances.filter(
            Q(student__first_name__icontains=q) |
            Q(student__last_name__icontains=q) |
            Q(student__admission_number__icontains=q)
        )

    total_expected = balances.aggregate(s=Sum('expected'))['s'] or 0
    total_paid = balances.aggregate(s=Sum('paid'))['s'] or 0
    total_balance = total_expected - total_paid

    context = {
        'balances': balances,
        'year': year,
        'term': term,
        'q': q,
        'total_expected': total_expected,
        'total_paid': total_paid,
        'total_balance': total_balance,
        'years': range(date.today().year, date.today().year - 4, -1),
    }
    return render(request, 'fees/fee_dashboard.html', context)


@login_required
@role_required('admin', 'bursar')
def payment_create(request):
    form = PaymentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        payment = form.save(commit=False)
        payment.received_by = request.user
        payment.save()
        # Update FeeBalance
        balance, _ = FeeBalance.objects.get_or_create(
            student=payment.student,
            term=payment.term,
            year=payment.year,
        )
        paid_total = FeePayment.objects.filter(
            student=payment.student, term=payment.term, year=payment.year
        ).aggregate(s=Sum('amount'))['s'] or 0
        balance.paid = paid_total
        if not balance.expected:
            try:
                structure = FeeStructure.objects.get(
                    stream=payment.student.class_section.stream,
                    term=payment.term,
                    year=payment.year,
                )
                balance.expected = structure.total
            except FeeStructure.DoesNotExist:
                pass
        balance.save()
        messages.success(request, f'Payment of KSh {payment.amount:,.0f} recorded for {payment.student.short_name}.')
        return redirect('fees:dashboard')
    return render(request, 'fees/payment_form.html', {'form': form, 'title': 'Record Payment'})


@login_required
@role_required('admin', 'bursar', 'auditor')
def payment_list(request):
    payments = FeePayment.objects.select_related('student', 'received_by').order_by('-date_paid')
    q = request.GET.get('q', '')
    if q:
        payments = payments.filter(
            Q(student__first_name__icontains=q) |
            Q(student__last_name__icontains=q) |
            Q(reference__icontains=q)
        )
    return render(request, 'fees/payment_list.html', {'payments': payments[:100], 'q': q})


@login_required
@role_required('admin', 'bursar')
def student_fee_detail(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    payments = FeePayment.objects.filter(student=student).order_by('-date_paid')
    balances = FeeBalance.objects.filter(student=student).order_by('-year', '-term')
    return render(request, 'fees/student_fee_detail.html', {
        'student': student, 'payments': payments, 'balances': balances
    })
