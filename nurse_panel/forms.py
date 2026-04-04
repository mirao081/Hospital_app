from django import forms
from core.models import Patient  # ✅ Use global patient model
from .models import Vitals, DailyRound
from .models import MedicationLog, MedicationRequest



class PatientForm(forms.ModelForm):
    # Include fields from the custom User model
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = Patient
        fields = ['age', 'gender', 'phone', 'address', 'username', 'first_name', 'last_name']

class VitalsForm(forms.ModelForm):
    class Meta:
        model = Vitals
        fields = ['patient', 'temperature', 'blood_pressure', 'heart_rate']


class DailyRoundForm(forms.ModelForm):
    class Meta:
        model = DailyRound
        fields = ['patient', 'notes']

class MedicationLogForm(forms.ModelForm):
    class Meta:
        model = MedicationLog
        fields = ['order', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.Select(attrs={'class': 'form-select'}),
        }


class MedicationRequestForm(forms.ModelForm):
    class Meta:
        model = MedicationRequest
        fields = ['medication_name', 'quantity']
        widgets = {
            'medication_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


