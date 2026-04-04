from django import forms
from core.models import SurveyResponse, Feedback
<<<<<<< HEAD
=======
from doctor_panel.models import PatientPortalRequest
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        fields = ['visit_date', 'satisfaction_score', 'comments']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'satisfaction_score': forms.RadioSelect(),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'subject', 'message']
        widgets = {
            'feedback_type': forms.Select(),
            'message': forms.Textarea(attrs={'rows': 4}),
<<<<<<< HEAD
=======
        }

class PatientPortalRequestForm(forms.ModelForm):
    class Meta:
        model = PatientPortalRequest
        fields = ['doctor', 'request_type', 'message']  # remove patient_name and patient_contact
        widgets = {
            "request_type": forms.Select(attrs={"class": "form-select"}),
            "message": forms.Textarea(attrs={"rows": 4, "class": "form-textarea"}),
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        }