from django import forms
from core.models import Patient  # ✅ Use global patient model
from .models import Vitals, DailyRound
from .models import MedicationLog, MedicationRequest
<<<<<<< HEAD



class PatientForm(forms.ModelForm):
    # Include fields from the custom User model
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = Patient
        fields = ['age', 'gender', 'phone', 'address', 'username', 'first_name', 'last_name']
=======
from core.models import Doctor
from django.contrib.auth import get_user_model

User = get_user_model()




# nurse_panel/forms.py
from django import forms
from core.models import Patient, User, Doctor

# nurse_panel/forms.py
from django import forms
from django.contrib.auth import get_user_model
from core.models import Patient
from core.models import Doctor  # adjust import if Doctor is elsewhere

User = get_user_model()

class PatientForm(forms.ModelForm):
    # user creation fields
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.select_related('user').all(),
        required=False,
        empty_label="Select Doctor (optional)"
    )

    referred_by = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['doctor','nurse','pharmacist','labtech']).order_by('first_name','last_name'),
        required=False,
        empty_label="-- Select staff (optional) --"
    )

    referral_details = forms.CharField(required=False, max_length=255)

    class Meta:
        model = Patient
        fields = [
            'age', 'gender', 'phone', 'address',
            'username', 'first_name', 'last_name', 'email',
            'doctor', 'referral_source', 'referred_by', 'referral_details'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['referral_source'].choices = Patient.REFERRAL_CHOICES

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

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


