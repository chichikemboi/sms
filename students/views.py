from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from accounts.decorators import role_required
from .models import Student, Guardian, ClassSection
from .forms import StudentForm, GuardianForm, StudentFilterForm


# ── Student list ──────────────────────────────────────────────────────────────

@login_required
@role_required('admin', 'class_teacher', 'subject_teacher', 'bursar')
def student_list(request):
    qs = Student.objects.select_related('class_section__stream', 'guardian')

    # Class teachers only see their own class
    if request.user.is_class_teacher and not request.user.is_admin:
        qs = qs.filter(class_section__class_teacher=request.user)

    filter_form = StudentFilterForm(request.GET)
    if filter_form.is_valid():
        q = filter_form.cleaned_data.get('q')
        section = filter_form.cleaned_data.get('class_section')
        status = filter_form.cleaned_data.get('status')
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(admission_number__icontains=q)
            )
        if section:
            qs = qs.filter(class_section=section)
        if status:
            qs = qs.filter(status=status)

    paginator = Paginator(qs, 30)
    page = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page,
        'filter_form': filter_form,
        'total': qs.count(),
    }
    return render(request, 'students/student_list.html', context)


# ── Student detail ────────────────────────────────────────────────────────────

@login_required
@role_required('admin', 'class_teacher', 'subject_teacher', 'bursar', 'parent')
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related(
        'class_section__stream', 'guardian', 'class_section__class_teacher'
    ), pk=pk)

    # Parents can only view their own child
    if request.user.is_parent:
        try:
            if student.guardian.user != request.user:
                messages.error(request, 'You can only view your own child\'s record.')
                return redirect('dashboard:home')
        except AttributeError:
            return redirect('dashboard:home')

    return render(request, 'students/student_detail.html', {'student': student})


# ── Create student ────────────────────────────────────────────────────────────

@login_required
@role_required('admin', 'class_teacher')
def student_create(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and student_form.is_valid():
        student = student_form.save()
        messages.success(request, f'{student.full_name} ({student.admission_number}) added successfully.')
        return redirect('students:detail', pk=student.pk)
    return render(request, 'students/student_form.html', {
        'form': student_form,
        'title': 'Enroll New Student',
    })


# ── Edit student ──────────────────────────────────────────────────────────────

@login_required
@role_required('admin', 'class_teacher')
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{student.full_name} updated successfully.')
        return redirect('students:detail', pk=student.pk)
    return render(request, 'students/student_form.html', {
        'form': form,
        'title': f'Edit: {student.full_name}',
        'student': student,
    })


# ── Guardian management ───────────────────────────────────────────────────────

@login_required
@role_required('admin', 'class_teacher')
def guardian_list(request):
    guardians = Guardian.objects.prefetch_related('students').order_by('last_name')
    q = request.GET.get('q', '')
    if q:
        guardians = guardians.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(phone_primary__icontains=q)
        )
    return render(request, 'students/guardian_list.html', {'guardians': guardians, 'q': q})


@login_required
@role_required('admin', 'class_teacher')
def guardian_create(request):
    form = GuardianForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        guardian = form.save()
        messages.success(request, f'Guardian {guardian.full_name} added.')
        next_url = request.GET.get('next', 'students:guardian_list')
        return redirect(next_url)
    return render(request, 'students/guardian_form.html', {'form': form, 'title': 'Add Guardian'})


@login_required
@role_required('admin', 'class_teacher')
def guardian_edit(request, pk):
    guardian = get_object_or_404(Guardian, pk=pk)
    form = GuardianForm(request.POST or None, instance=guardian)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{guardian.full_name} updated.')
        return redirect('students:guardian_list')
    return render(request, 'students/guardian_form.html', {
        'form': form,
        'title': f'Edit Guardian: {guardian.full_name}',
    })
