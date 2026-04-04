from django import forms
from django.utils import timezone
from .models import User, Appointment, Blog, Enquiry, Message, RefundRequest, Bed, Patient, Room


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AppointmentForm(forms.ModelForm):
    datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Appointment Date & Time',
    )

    class Meta:
        model = Appointment
        fields = ['full_name', 'email', 'phone', 'doctor', 'datetime', 'reason', 'comment']

        labels = {
            'reason': 'Reason for Appointment',
            'comment': 'Description',
        }

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={
                'class': 'form-control',
                'style': 'color: black; background-color: white; border: 1px solid #000;',
            }),
            'reason': forms.TextInput(attrs={
                'placeholder': 'e.g. Consultation, Follow-up, etc.',
                'class': 'form-control',
            }),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Describe your issue...',
                'class': 'form-control',
                'rows': 3,
            }),
        }

    def clean_datetime(self):
        dt = self.cleaned_data['datetime']
        if timezone.is_naive(dt):
            # Make aware in current timezone
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'image', 'category']


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'phone', 'country', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Write your message here', 'rows': 5})
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-input'}),
            'body': forms.Textarea(attrs={'class': 'form-textarea'}),
        }

    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        if sender:
            self.fields['recipient'].queryset = User.objects.exclude(id=sender.id)


class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['refund_amount', 'reason']  # removed 'payment'

        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'refund_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AssignBedForm(forms.Form):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), label="Select Patient")
    room = forms.ModelChoiceField(queryset=Room.objects.all(), label="Select Room")
    bed = forms.ModelChoiceField(queryset=Bed.objects.filter(is_occupied=False), label="Select Bed")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bed'].queryset = Bed.objects.filter(is_occupied=False, patient__isnull=True)
