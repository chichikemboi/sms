from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Q
from django import forms as django_forms

from accounts.decorators import role_required, teacher_required
from students.models import ClassSection, Student
from .models import Exam, Subject, Mark, TeacherSubjectAssignment, get_kcse_grade


# ── Exam list ─────────────────────────────────────────────────────────────────

@login_required
@teacher_required
def exam_list(request):
    exams = Exam.objects.prefetch_related('streams').order_by('-year', '-term')
    return render(request, 'exams/exam_list.html', {'exams': exams})


# ── Exam create ───────────────────────────────────────────────────────────────

@login_required
@role_required('admin')
def exam_create(request):
    from .forms import ExamForm
    form = ExamForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        exam = form.save(commit=False)
        exam.created_by = request.user
        exam.save()
        form.save_m2m()
        messages.success(request, f'Exam "{exam.name}" created.')
        return redirect('exams:list')
    return render(request, 'exams/exam_form.html', {'form': form, 'title': 'Create Exam'})


# ── Mark entry grid ───────────────────────────────────────────────────────────

@login_required
@teacher_required
def mark_entry(request, exam_pk, section_pk, subject_pk):
    exam = get_object_or_404(Exam, pk=exam_pk)
    section = get_object_or_404(ClassSection, pk=section_pk)
    subject = get_object_or_404(Subject, pk=subject_pk)

    # Permission: subject teachers only enter their own subjects
    if request.user.is_subject_teacher and not request.user.is_admin:
        assigned = TeacherSubjectAssignment.objects.filter(
            teacher=request.user, subject=subject, class_section=section
        ).exists()
        if not assigned:
            messages.error(request, 'You are not assigned to this subject/class.')
            return redirect('exams:list')

    students = Student.objects.filter(
        class_section=section, status='active'
    ).order_by('last_name', 'first_name')

    # Pre-fetch existing marks
    existing = {
        m.student_id: m
        for m in Mark.objects.filter(exam=exam, subject=subject, student__in=students)
    }

    if request.method == 'POST':
        saved = 0
        for student in students:
            score_key = f'score_{student.pk}'
            absent_key = f'absent_{student.pk}'
            is_absent = absent_key in request.POST
            raw_score = request.POST.get(score_key, '').strip()

            mark, _ = Mark.objects.get_or_create(
                exam=exam, student=student, subject=subject,
                defaults={'entered_by': request.user}
            )
            mark.is_absent = is_absent
            mark.entered_by = request.user
            if is_absent:
                mark.score = None
            else:
                try:
                    mark.score = float(raw_score) if raw_score else None
                except ValueError:
                    mark.score = None
            mark.save()
            saved += 1

        messages.success(request, f'Marks saved for {saved} students.')
        return redirect('exams:mark_entry', exam_pk=exam_pk, section_pk=section_pk, subject_pk=subject_pk)

    # Build rows for template
    rows = []
    for student in students:
        mark = existing.get(student.pk)
        rows.append({
            'student': student,
            'mark': mark,
            'score': mark.score if mark else '',
            'is_absent': mark.is_absent if mark else False,
            'grade': mark.grade if mark else '—',
        })

    context = {
        'exam': exam,
        'section': section,
        'subject': subject,
        'rows': rows,
        'max_score': subject.max_score,
    }
    return render(request, 'exams/mark_entry.html', context)


# ── Mark entry selector ───────────────────────────────────────────────────────

@login_required
@teacher_required
def mark_entry_select(request, exam_pk):
    exam = get_object_or_404(Exam, pk=exam_pk)

    if request.user.is_admin:
        sections = ClassSection.objects.filter(
            stream__in=exam.streams.all()
        ).select_related('stream')
        subjects = Subject.objects.all()
    else:
        assignments = TeacherSubjectAssignment.objects.filter(
            teacher=request.user,
            class_section__stream__in=exam.streams.all()
        ).select_related('subject', 'class_section__stream')
        sections = ClassSection.objects.filter(
            pk__in=assignments.values_list('class_section', flat=True)
        ).distinct()
        subjects = Subject.objects.filter(
            pk__in=assignments.values_list('subject', flat=True)
        ).distinct()

    context = {'exam': exam, 'sections': sections, 'subjects': subjects}
    return render(request, 'exams/mark_entry_select.html', context)


# ── Results / analysis ────────────────────────────────────────────────────────

@login_required
@teacher_required
def results_analysis(request, exam_pk, section_pk):
    exam = get_object_or_404(Exam, pk=exam_pk)
    section = get_object_or_404(ClassSection.objects.select_related('stream'), pk=section_pk)

    students = Student.objects.filter(
        class_section=section, status='active'
    ).order_by('last_name', 'first_name')

    subjects = Subject.objects.filter(
        marks__exam=exam, marks__student__in=students
    ).distinct().order_by('order')

    # Build pivot: student → {subject_id: mark}
    marks_qs = Mark.objects.filter(
        exam=exam, student__in=students, subject__in=subjects
    ).select_related('student', 'subject')

    pivot = {}
    for m in marks_qs:
        pivot.setdefault(m.student_id, {})[m.subject_id] = m

    rows = []
    for student in students:
        student_marks = pivot.get(student.pk, {})
        subject_scores = []
        total_pts = 0
        scored_subjects = 0
        for subj in subjects:
            mark = student_marks.get(subj.pk)
            if mark and not mark.is_absent and mark.score is not None:
                score = float(mark.score)
                grade, pts = get_kcse_grade(score)
                subject_scores.append({'score': score, 'grade': grade, 'points': pts})
                total_pts += pts
                scored_subjects += 1
            elif mark and mark.is_absent:
                subject_scores.append({'score': 'ABS', 'grade': 'ABS', 'points': 0})
            else:
                subject_scores.append({'score': '—', 'grade': '—', 'points': 0})

        mean_pts = round(total_pts / scored_subjects, 3) if scored_subjects else 0
        mean_grade, _ = get_kcse_grade(mean_pts * (100 / 12))
        rows.append({
            'student': student,
            'scores': subject_scores,
            'total_pts': total_pts,
            'mean_pts': mean_pts,
            'mean_grade': mean_grade,
        })

    # Sort by mean points descending, assign positions
    rows.sort(key=lambda r: r['mean_pts'], reverse=True)
    for i, row in enumerate(rows, 1):
        row['position'] = i

    # Subject stats
    subject_stats = []
    for subj in subjects:
        subj_marks = [
            float(m.score)
            for m in marks_qs
            if m.subject_id == subj.pk and not m.is_absent and m.score is not None
        ]
        if subj_marks:
            subject_stats.append({
                'subject': subj,
                'avg': round(sum(subj_marks) / len(subj_marks), 1),
                'highest': max(subj_marks),
                'lowest': min(subj_marks),
                'entries': len(subj_marks),
            })

    context = {
        'exam': exam,
        'section': section,
        'subjects': subjects,
        'rows': rows,
        'subject_stats': subject_stats,
    }
    return render(request, 'exams/results_analysis.html', context)
