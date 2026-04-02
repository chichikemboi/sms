from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from datetime import date, timedelta

from accounts.decorators import role_required, teacher_required
from students.models import Student, ClassSection
from .models import AttendanceRecord


@login_required
@teacher_required
def attendance_home(request):
    sections = ClassSection.objects.select_related('stream').order_by('stream__order', 'section')
    if request.user.is_class_teacher and not request.user.is_admin:
        sections = sections.filter(class_teacher=request.user)
    return render(request, 'attendance/home.html', {'sections': sections})


@login_required
@teacher_required
def mark_attendance(request, section_pk):
    section = get_object_or_404(ClassSection, pk=section_pk)
    selected_date = request.GET.get('date', date.today().isoformat())
    try:
        att_date = date.fromisoformat(selected_date)
    except ValueError:
        att_date = date.today()

    students = Student.objects.filter(
        class_section=section, status='active'
    ).order_by('last_name', 'first_name')

    existing = {
        r.student_id: r
        for r in AttendanceRecord.objects.filter(student__in=students, date=att_date)
    }

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.pk}', 'P')
            notes = request.POST.get(f'notes_{student.pk}', '')
            record, _ = AttendanceRecord.objects.get_or_create(
                student=student, date=att_date,
                defaults={'marked_by': request.user}
            )
            record.status = status
            record.notes = notes
            record.marked_by = request.user
            record.save()
        messages.success(request, f'Attendance saved for {section} on {att_date.strftime("%d %b %Y")}.')
        return redirect('attendance:mark', section_pk=section_pk)

    rows = []
    for student in students:
        rec = existing.get(student.pk)
        rows.append({'student': student, 'record': rec, 'status': rec.status if rec else 'P'})

    context = {
        'section': section,
        'att_date': att_date,
        'rows': rows,
        'status_choices': AttendanceRecord.STATUS_CHOICES,
        'prev_date': (att_date - timedelta(days=1)).isoformat(),
        'next_date': (att_date + timedelta(days=1)).isoformat(),
        'is_today': att_date == date.today(),
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
@teacher_required
def attendance_report(request, section_pk):
    section = get_object_or_404(ClassSection, pk=section_pk)
    students = Student.objects.filter(class_section=section, status='active')

    records = AttendanceRecord.objects.filter(student__in=students).values(
        'student_id', 'status'
    ).annotate(count=Count('id'))

    stats = {}
    for r in records:
        sid = r['student_id']
        if sid not in stats:
            stats[sid] = {'P': 0, 'A': 0, 'L': 0, 'E': 0}
        stats[sid][r['status']] = r['count']

    rows = []
    for student in students.order_by('last_name'):
        s = stats.get(student.pk, {'P': 0, 'A': 0, 'L': 0, 'E': 0})
        total = sum(s.values())
        rate = round((s['P'] + s['L']) / total * 100, 1) if total else 0
        rows.append({'student': student, 'stats': s, 'total': total, 'rate': rate})

    rows.sort(key=lambda r: r['rate'])

    return render(request, 'attendance/report.html', {'section': section, 'rows': rows})
