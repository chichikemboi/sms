from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from datetime import date

from accounts.decorators import teacher_required, admin_required
from students.models import ClassSection
from exams.models import Subject
from .models import LessonPlan, SyllabusUnit, TopicCoverage
from .forms import LessonPlanForm


@login_required
@teacher_required
def lesson_list(request):
    plans = LessonPlan.objects.select_related('subject', 'class_section__stream', 'teacher')
    if not request.user.is_admin:
        plans = plans.filter(teacher=request.user)

    term = request.GET.get('term', '')
    year = request.GET.get('year', date.today().year)
    if term:
        plans = plans.filter(term=term)
    if year:
        plans = plans.filter(year=year)

    context = {
        'plans': plans.order_by('-year', '-term', 'week_number'),
        'sel_term': term,
        'sel_year': int(year),
        'years': range(date.today().year, date.today().year - 3, -1),
    }
    return render(request, 'lessons/lesson_list.html', context)


@login_required
@teacher_required
def lesson_create(request):
    form = LessonPlanForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        plan = form.save(commit=False)
        plan.teacher = request.user
        plan.save()
        messages.success(request, f'Lesson plan for "{plan.topic}" saved.')
        return redirect('lessons:list')
    return render(request, 'lessons/lesson_form.html', {'form': form, 'title': 'New Lesson Plan'})


@login_required
@teacher_required
def lesson_edit(request, pk):
    plan = get_object_or_404(LessonPlan, pk=pk)
    if not request.user.is_admin and plan.teacher != request.user:
        messages.error(request, 'You can only edit your own lesson plans.')
        return redirect('lessons:list')
    form = LessonPlanForm(request.POST or None, instance=plan, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lesson plan updated.')
        return redirect('lessons:list')
    return render(request, 'lessons/lesson_form.html', {
        'form': form, 'title': f'Edit Plan: {plan.topic}', 'plan': plan
    })


@login_required
@teacher_required
def lesson_detail(request, pk):
    plan = get_object_or_404(LessonPlan.objects.select_related(
        'subject', 'class_section__stream', 'teacher', 'unit'
    ), pk=pk)
    return render(request, 'lessons/lesson_detail.html', {'plan': plan})


@login_required
@teacher_required
def syllabus_coverage(request, section_pk, subject_pk):
    section = get_object_or_404(ClassSection, pk=section_pk)
    subject = get_object_or_404(Subject, pk=subject_pk)
    term = int(request.GET.get('term', 1))
    year = int(request.GET.get('year', date.today().year))

    units = SyllabusUnit.objects.filter(
        subject=subject, stream=section.stream
    ).order_by('order')

    existing = {
        c.unit_id: c
        for c in TopicCoverage.objects.filter(
            class_section=section, term=term, year=year,
            unit__subject=subject
        )
    }

    if request.method == 'POST':
        for unit in units:
            is_covered = f'covered_{unit.pk}' in request.POST
            date_str = request.POST.get(f'date_{unit.pk}', '')
            notes = request.POST.get(f'notes_{unit.pk}', '')
            coverage, _ = TopicCoverage.objects.get_or_create(
                unit=unit, class_section=section, term=term, year=year,
                defaults={'teacher': request.user}
            )
            coverage.is_covered = is_covered
            coverage.notes = notes
            coverage.teacher = request.user
            if is_covered and date_str:
                try:
                    coverage.date_covered = date.fromisoformat(date_str)
                except ValueError:
                    coverage.date_covered = date.today()
            elif is_covered and not coverage.date_covered:
                coverage.date_covered = date.today()
            coverage.save()
        messages.success(request, 'Syllabus coverage updated.')
        return redirect(request.path + f'?term={term}&year={year}')

    rows = [{'unit': u, 'coverage': existing.get(u.pk)} for u in units]
    covered_count = sum(1 for r in rows if r['coverage'] and r['coverage'].is_covered)
    pct = round(covered_count / len(rows) * 100) if rows else 0

    context = {
        'section': section, 'subject': subject, 'rows': rows,
        'term': term, 'year': year, 'covered_count': covered_count,
        'total': len(rows), 'pct': pct,
        'years': range(date.today().year, date.today().year - 3, -1),
    }
    return render(request, 'lessons/syllabus_coverage.html', context)


@login_required
@teacher_required
def coverage_home(request):
    sections = ClassSection.objects.select_related('stream').order_by('stream__order', 'section')
    subjects = Subject.objects.all()
    if not request.user.is_admin:
        from exams.models import TeacherSubjectAssignment
        assignments = TeacherSubjectAssignment.objects.filter(teacher=request.user)
        sections = sections.filter(pk__in=assignments.values_list('class_section', flat=True))
        subjects = subjects.filter(pk__in=assignments.values_list('subject', flat=True))
    return render(request, 'lessons/coverage_home.html', {
        'sections': sections, 'subjects': subjects
    })
