from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.conf import settings

from accounts.decorators import role_required
from students.models import Student, ClassSection
from exams.models import Exam, Mark, get_kcse_grade
from fees.models import FeePayment, FeeBalance
from .pdf_generator import generate_report_card, generate_fee_statement


@login_required
@role_required('admin', 'class_teacher')
def letters_home(request):
    exams = Exam.objects.order_by('-year', '-term')
    sections = ClassSection.objects.select_related('stream').order_by('stream__order', 'section')
    return render(request, 'letters/letters_home.html', {
        'exams': exams, 'sections': sections
    })


@login_required
@role_required('admin', 'class_teacher', 'parent')
def report_card_pdf(request, student_pk, exam_pk):
    student = get_object_or_404(Student.objects.select_related(
        'class_section__stream', 'class_section__class_teacher', 'guardian'
    ), pk=student_pk)
    exam = get_object_or_404(Exam, pk=exam_pk)

    # Parents can only access their child
    if request.user.is_parent:
        try:
            if student.guardian.user != request.user:
                raise Http404
        except AttributeError:
            raise Http404

    # Fetch marks for this student
    marks_qs = Mark.objects.filter(
        exam=exam, student=student
    ).select_related('subject').order_by('subject__order')

    marks_data = []
    for m in marks_qs:
        score = float(m.score) if m.score is not None else None
        grade, points = get_kcse_grade(score) if not m.is_absent and score is not None else ('ABS', 0)
        marks_data.append({
            'subject': m.subject,
            'score': score,
            'grade': 'ABS' if m.is_absent else grade,
            'points': 0 if m.is_absent else points,
        })

    # Compute position in class
    all_marks = Mark.objects.filter(
        exam=exam,
        student__class_section=student.class_section,
        student__status='active',
    ).select_related('student')

    student_pts = {}
    for m in all_marks:
        sid = m.student_id
        if sid not in student_pts:
            student_pts[sid] = 0
        if not m.is_absent and m.score is not None:
            _, pts = get_kcse_grade(float(m.score))
            student_pts[sid] += pts

    sorted_students = sorted(student_pts.items(), key=lambda x: x[1], reverse=True)
    position = next((i + 1 for i, (sid, _) in enumerate(sorted_students) if sid == student.pk), '—')
    total_students = len(sorted_students)

    pdf_bytes = generate_report_card(
        student=student,
        exam=exam,
        marks_data=marks_data,
        position=position,
        total_students=total_students,
        school_name=settings.SCHOOL_NAME,
        school_motto=settings.SCHOOL_MOTTO,
        class_teacher_name=student.class_section.class_teacher.get_full_name()
            if student.class_section.class_teacher else '',
        teacher_remarks=request.GET.get('teacher_remarks', ''),
        principal_remarks=request.GET.get('principal_remarks', ''),
    )

    filename = f'report_card_{student.admission_number}_{exam.term}_{exam.year}.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@login_required
@role_required('admin', 'bursar', 'class_teacher', 'parent')
def fee_statement_pdf(request, student_pk):
    student = get_object_or_404(Student.objects.select_related('class_section__stream'), pk=student_pk)

    if request.user.is_parent:
        try:
            if student.guardian.user != request.user:
                raise Http404
        except AttributeError:
            raise Http404

    payments = FeePayment.objects.filter(student=student).order_by('-date_paid')
    balances = FeeBalance.objects.filter(student=student).order_by('-year', '-term')

    pdf_bytes = generate_fee_statement(
        student=student,
        payments=list(payments),
        balances=list(balances),
        school_name=settings.SCHOOL_NAME,
        school_motto=settings.SCHOOL_MOTTO,
    )

    filename = f'fee_statement_{student.admission_number}.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@login_required
@role_required('admin', 'class_teacher')
def class_report_cards(request, exam_pk, section_pk):
    """Render a page with links to all individual report cards in a class."""
    exam = get_object_or_404(Exam, pk=exam_pk)
    section = get_object_or_404(ClassSection, pk=section_pk)
    students = Student.objects.filter(
        class_section=section, status='active'
    ).order_by('last_name', 'first_name')
    return render(request, 'letters/class_report_cards.html', {
        'exam': exam, 'section': section, 'students': students
    })
