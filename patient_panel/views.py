from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Appointment
from core.models import Patient
from .models import Diagnosis, Treatment, Medication, LabResult, Visit,Bill
from django.utils import timezone
from .forms import SurveyResponseForm
from .forms import FeedbackForm
from core.models import Feedback
from django.contrib import messages
from core.models import Message,Patient
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def patient_dashboard(request):
    patient = get_object_or_404(Patient, user=request.user)

    diagnoses = patient.diagnoses.all()
    treatments = patient.treatments.all()
    medications = patient.medications.all()
    lab_results = patient.lab_results.all()

    today = timezone.now().date()  # Only date portion

    # Visits - compare date with date
    upcoming_visits = patient.visits.filter(visit_date__gte=today).order_by('visit_date')
    past_visits = patient.visits.filter(visit_date__lt=today).order_by('-visit_date')

    # Bills
    outstanding_bills = patient.user.bills.filter(is_paid=False)
    paid_bills = patient.user.bills.filter(is_paid=True)

    now = timezone.now()

    # Appointments filtered correctly on datetime field
    upcoming_appointments = patient.appointments.filter(datetime__gte=now).order_by('datetime')
    past_appointments = patient.appointments.filter(datetime__lt=now).order_by('-datetime')

    context = {
        'diagnoses': diagnoses,
        'treatments': treatments,
        'medications': medications,
        'lab_results': lab_results,
        'upcoming_visits': upcoming_visits,
        'past_visits': past_visits,
        'outstanding_bills': outstanding_bills,
        'paid_bills': paid_bills,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'payment_history': paid_bills,
    }
    return render(request, 'patient_panel/dashboard.html', context)

@login_required
def submit_survey(request):
    patient = Patient.objects.get(user=request.user)

    if request.method == 'POST':
        form = SurveyResponseForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.patient = patient
            survey.save()

            # ✅ Notify all staff or admin group users
            try:
                staff_group = Group.objects.get(name='Staff')  # Replace with actual group name
                staff_users = staff_group.user_set.all()
            except Group.DoesNotExist:
                staff_users = User.objects.filter(is_staff=True)

            for staff in staff_users:
                Message.objects.create(
                    sender=request.user,
                    recipient=staff,
                    subject="📝 New Patient Survey Submitted",
                    body=survey.comments or "A new survey has been submitted by a patient."  # ✅ using `body`
                )

            messages.success(request, "Survey submitted successfully!")
            return redirect('patient_panel:patient_dashboard')
    else:
        form = SurveyResponseForm()

    return render(request, 'patient_panel/submit_survey.html', {'form': form})


@login_required
def submit_feedback(request):
    patient = Patient.objects.get(user=request.user)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.patient = patient
            feedback.save()

            try:
                staff_group = Group.objects.get(name='Staff')
                staff_users = staff_group.user_set.all()
            except Group.DoesNotExist:
                staff_users = User.objects.filter(is_staff=True)

            for staff in staff_users:
                Message.objects.create(
                    sender=request.user,
                    recipient=staff,
                    subject="💬 New Feedback Submitted",
                    body=feedback.message  # ✅ using `body`, not `message`
                )

            messages.success(request, "Feedback submitted successfully!")
            return redirect('patient_panel:patient_dashboard')
    else:
        form = FeedbackForm()

    return render(request, 'patient_panel/submit_feedback.html', {'form': form})