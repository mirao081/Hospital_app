from django import forms
from .models import Medicine,Prescription

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'batch_number', 'stock', 'expiry_date', 'category']


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient_name', 'doctor_name', 'medicine', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
