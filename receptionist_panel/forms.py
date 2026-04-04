from django import forms
from django.core.exceptions import ValidationError
from core.models import Patient,Appointment  

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['age', 'gender', 'phone', 'address', 'referral_source']
        widgets = {
            'referral_source': forms.Select(attrs={
                'class': 'w-full border rounded-md p-2'
            }),
        }
        labels = {
            'referral_source': 'How did the patient hear about the hospital?'
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }
