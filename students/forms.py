from django import forms
from .models import Student, Guardian, ClassSection


class GuardianForm(forms.ModelForm):
    class Meta:
        model = Guardian
        fields = [
            'first_name', 'last_name', 'relation', 'phone_primary',
            'phone_secondary', 'email', 'id_number', 'occupation', 'address',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 2})
            else:
                field.widget.attrs['class'] = 'form-control'


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'admission_number', 'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'gender', 'photo', 'kcpe_index', 'kcpe_marks', 'nemis_no',
            'class_section', 'date_admitted', 'boarding_type', 'status',
            'guardian', 'medical_notes', 'special_needs', 'notes',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_admitted': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'medical_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'special_needs': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, (forms.Select,)):
                w.attrs.setdefault('class', 'form-select')
            elif not isinstance(w, (forms.FileInput, forms.DateInput, forms.Textarea)):
                w.attrs.setdefault('class', 'form-control')
        self.fields['class_section'].queryset = (
            ClassSection.objects.select_related('stream').order_by('stream__order', 'section')
        )
        self.fields['guardian'].queryset = (
            Guardian.objects.order_by('last_name', 'first_name')
        )


class StudentFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search name or admission no...',
    }))
    class_section = forms.ModelChoiceField(
        queryset=ClassSection.objects.select_related('stream').order_by('stream__order', 'section'),
        required=False,
        empty_label='All Classes',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Student.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
