from django import forms
from core.models import SurveyResponse, Feedback

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
        }