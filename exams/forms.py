from django import forms
from .models import Exam, Subject, TeacherSubjectAssignment


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'exam_type', 'term', 'year', 'streams', 'date_start', 'date_end']
        widgets = {
            'date_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'streams': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.Select):
                w.attrs.setdefault('class', 'form-select')
            elif not isinstance(w, (forms.DateInput, forms.CheckboxSelectMultiple)):
                w.attrs.setdefault('class', 'form-control')


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'curriculum', 'is_compulsory', 'max_score', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.Select):
                w.attrs['class'] = 'form-select'
            elif isinstance(w, forms.CheckboxInput):
                w.attrs['class'] = 'form-check-input'
            else:
                w.attrs['class'] = 'form-control'


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignment
        fields = ['teacher', 'subject', 'class_section']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select'
