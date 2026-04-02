from django import forms
from .models import StaffProfile


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = [
            'tsc_number', 'national_id', 'employment_status', 'date_joined',
            'subjects_taught', 'qualification', 'specialization',
            'emergency_contact_name', 'emergency_contact_phone',
            'bank_name', 'bank_account', 'notes',
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'subjects_taught': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.Select):
                w.attrs.setdefault('class', 'form-select')
            elif not isinstance(w, (forms.DateInput, forms.CheckboxSelectMultiple, forms.Textarea)):
                w.attrs.setdefault('class', 'form-control')
