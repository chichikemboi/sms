from django import forms
from .models import LessonPlan, SyllabusUnit, TopicCoverage


class LessonPlanForm(forms.ModelForm):
    class Meta:
        model = LessonPlan
        fields = [
            'subject', 'class_section', 'unit', 'week_number', 'term', 'year',
            'topic', 'objectives', 'content_outline', 'teaching_methods',
            'resources', 'assessment', 'remarks', 'status',
        ]
        widgets = {
            'objectives': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'content_outline': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'resources': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'assessment': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.Select):
                w.attrs.setdefault('class', 'form-select')
            elif not isinstance(w, forms.Textarea):
                w.attrs.setdefault('class', 'form-control')
        # Non-admins can only create plans for themselves
        if user and not user.is_admin:
            from students.models import ClassSection
            from exams.models import Subject
            from exams.models import TeacherSubjectAssignment
            assigned = TeacherSubjectAssignment.objects.filter(teacher=user)
            self.fields['subject'].queryset = Subject.objects.filter(
                pk__in=assigned.values_list('subject', flat=True)
            )
            self.fields['class_section'].queryset = ClassSection.objects.filter(
                pk__in=assigned.values_list('class_section', flat=True)
            )
