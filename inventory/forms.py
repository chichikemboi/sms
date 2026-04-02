from django import forms
from .models import InventoryItem, InventoryCategory


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['category', 'name', 'description', 'quantity', 'condition',
                  'location', 'serial_number', 'date_acquired', 'value_kes', 'notes']
        widgets = {
            'date_acquired': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.Select):
                w.attrs.setdefault('class', 'form-select')
            elif not isinstance(w, (forms.DateInput, forms.Textarea)):
                w.attrs.setdefault('class', 'form-control')
