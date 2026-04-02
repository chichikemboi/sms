from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django import forms as django_forms

from accounts.decorators import admin_required, teacher_required
from students.models import ClassSection
from .models import Period, TimetableSlot
from exams.models import Subject
from accounts.models import User


class SlotForm(django_forms.ModelForm):
    class Meta:
        model = TimetableSlot
        fields = ['subject', 'teacher', 'room']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.all()
        self.fields['subject'].required = False
        self.fields['teacher'].queryset = User.objects.filter(
            role__in=['subject_teacher', 'class_teacher', 'admin'], is_active=True
        ).order_by('last_name')
        self.fields['teacher'].required = False
        for field in self.fields.values():
            if isinstance(field.widget, django_forms.Select):
                field.widget.attrs['class'] = 'form-select form-select-sm'
            else:
                field.widget.attrs['class'] = 'form-control form-control-sm'


@login_required
@teacher_required
def timetable_home(request):
    sections = ClassSection.objects.select_related('stream').order_by('stream__order', 'section')
    return render(request, 'timetable/home.html', {'sections': sections})


@login_required
@teacher_required
def timetable_view(request, section_pk):
    section = get_object_or_404(ClassSection.objects.select_related('stream'), pk=section_pk)
    periods = Period.objects.all()
    days = TimetableSlot.DAY_CHOICES

    # Build grid: {day: {period_id: slot}}
    slots = TimetableSlot.objects.filter(
        class_section=section
    ).select_related('subject', 'teacher', 'period')

    grid = {day: {} for day, _ in days}
    for slot in slots:
        grid[slot.day][slot.period_id] = slot

    context = {
        'section': section,
        'periods': periods,
        'days': days,
        'grid': grid,
        'can_edit': request.user.is_admin,
    }
    return render(request, 'timetable/timetable_view.html', context)


@admin_required
def slot_edit(request, section_pk, day, period_pk):
    section = get_object_or_404(ClassSection, pk=section_pk)
    period = get_object_or_404(Period, pk=period_pk)

    slot, _ = TimetableSlot.objects.get_or_create(
        class_section=section, day=day, period=period
    )
    form = SlotForm(request.POST or None, instance=slot)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Timetable slot updated.')
        return redirect('timetable:view', section_pk=section_pk)

    day_name = dict(TimetableSlot.DAY_CHOICES).get(day, '')
    return render(request, 'timetable/slot_edit.html', {
        'form': form, 'section': section,
        'period': period, 'day_name': day_name,
    })
