from django import forms
from .models import MedicalRecord

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
<<<<<<< HEAD
        fields = ['patient', 'diagnosis']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
        }
=======
        fields = [
            'patient', 'doctor', 'appointment',
            'patient_age', 'patient_gender', 'patient_contact', 'patient_insurance',
            'diagnosis', 'medications', 'prescription', 'lab_results', 'notes', 'imaging',
            'last_visit', 'last_prescription', 'last_lab_results', 'critical_alerts',
            'pending_tests', 'medication_management',
        ]
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 2}),
            'prescription': forms.Textarea(attrs={'rows': 2}),
            'lab_results': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'last_prescription': forms.Textarea(attrs={'rows': 2}),
            'last_lab_results': forms.Textarea(attrs={'rows': 2}),
            'critical_alerts': forms.Textarea(attrs={'rows': 2}),
            'pending_tests': forms.Textarea(attrs={'rows': 2}),
            'medication_management': forms.Textarea(attrs={'rows': 2}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.patient:
            if instance.patient_age is None:
                instance.patient_age = instance.patient.age
            if not instance.patient_gender:
                instance.patient_gender = instance.patient.gender
            if not instance.patient_contact:
                instance.patient_contact = instance.patient.phone
            if not instance.patient_insurance:
                instance.patient_insurance = ""
        if commit:
            instance.save()
            return instance
    
        def clean(self):
            cleaned_data = super().clean()
            age = cleaned_data.get('patient_age')
            if age is not None and age < 0:
                self.add_error('patient_age', 'Age cannot be negative.')
            return cleaned_data

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
