from django import forms
from .models import MedicalRecord

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['patient', 'diagnosis']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
        }
