from django import forms
from core.models import User
from django.contrib.auth.forms import UserCreationForm
from core.models import Message
from django.contrib.auth import get_user_model
from .models import RevenueAging,ClinicalMetric

class AdminRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True, label="Role")

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']
        labels = {
            'username': 'Username',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
        help_texts = {
            'username': '',
            'password1': '',
            'password2': '',
        }

    def __init__(self, *args, **kwargs):
        super(AdminRegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400',
            })

class RevenueAgingForm(forms.ModelForm):
    class Meta:
        model = RevenueAging
        exclude = ['bill_reference']  # <--- Hides it from the form

class ClinicalMetricForm(forms.ModelForm):
    class Meta:
        model = ClinicalMetric
        fields = ['metric_type', 'description', 'value']