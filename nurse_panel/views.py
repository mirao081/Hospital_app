from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from core.forms import MessageForm
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from core.models import Patient,Message  # ✅ Use the central Patient model
from .models import Vitals, DailyRound, Reminder
from .forms import VitalsForm, DailyRoundForm, PatientForm
from .models import NurseTask
from django.contrib.auth import get_user_model
from .models import MedicationOrder, MedicationLog, MedicationRequest
from .forms import MedicationLogForm, MedicationRequestForm
from doctor_panel.utils import get_comm_context
from doctor_panel.models import ReferralRequest
from django.db.models import Q
User = get_user_model()






@login_required
def nurse_dashboard(request):
    user = request.user
    if user.role != 'nurse':
        return render(request, '403.html')

    # Medication-related context
    medication_orders = MedicationOrder.objects.all().order_by('-start_date')
    medication_logs = MedicationLog.objects.filter(administered_by=user)
    med_requests = MedicationRequest.objects.filter(nurse=user)
    
    # Referrals for this nurse
    referrals = ReferralRequest.objects.filter(
        Q(to_nurse=user) | Q(from_doctor__isnull=False)
    ).order_by('-created_at')

    context = {
        'medication_orders': medication_orders,
        'medication_logs': medication_logs,
        'med_requests': med_requests,
        'referrals': referrals,  # for partial
    }

    # ✅ pass the user to get_comm_context
    context.update(get_comm_context(user=user, scope="all", limit=5))

    # ✅ no need to override referrals again unless you want to force only nurse ones
    # context['referrals'] = referrals  

    return render(request, 'nurse_panel/dashboard.html', context)
# View all patients
@login_required
def nurse_patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'nurse_panel/patient_list.html', {'patients': patients})


# Add new patient (if allowed from nurse panel)
@login_required
def add_nurse_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = 'default123'

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' is already taken.")
                return render(request, 'nurse_panel/patient_form.html', {'form': form})

            try:
                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                patient = form.save(commit=False)
                patient.user = user
                patient.save()
                messages.success(request, f"Patient '{first_name} {last_name}' added.")
                return redirect('nurse_panel:nurse_patient_list')

            except IntegrityError:
                messages.error(request, "Something went wrong. Please try again.")
    else:
        form = PatientForm()
    return render(request, 'nurse_panel/patient_form.html', {'form': form})

# View a patient's full profile
@login_required
def nurse_patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    vitals = Vitals.objects.filter(patient=patient).order_by('-recorded_at')
    rounds = DailyRound.objects.filter(patient=patient).order_by('-recorded_at')
    reminders = Reminder.objects.filter(patient=patient).order_by('scheduled_time')

    context = {
        'patient': patient,
        'vitals': vitals,
        'rounds': rounds,
        'reminders': reminders,
    }
    return render(request, 'nurse_panel/patient_detail.html', context)


# Add vitals for a patient
@login_required
def add_vitals(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        temperature = request.POST.get('temperature')
        blood_pressure = request.POST.get('blood_pressure')
        heart_rate = request.POST.get('heart_rate')

        # Optional: validate fields here

        Vitals.objects.create(
            patient=patient,
            temperature=temperature,
            blood_pressure=blood_pressure,
            heart_rate=heart_rate,
            nurse=request.user
        )

        messages.success(request, f'Vitals for {patient.full_name} saved.')
        return redirect('nurse_panel:nurse_patient_detail', patient_id=patient.id)

    return render(request, 'nurse_panel/add_vitals.html', {'patient': patient})


# Log daily round notes
@login_required
def log_daily_round(request):
    if request.method == 'POST':
        form = DailyRoundForm(request.POST)
        if form.is_valid():
            round_instance = form.save(commit=False)
            round_instance.nurse = request.user
            round_instance.save()
            messages.success(request, "Daily round logged.")
            return redirect('nurse_panel:log_daily_round')
    else:
        form = DailyRoundForm()
    return render(request, 'nurse_panel/log_daily_round.html', {'form': form})


# Medication reminders
@login_required
def view_reminders(request):
    query = request.GET.get('q', '')
    now = timezone.now()

    upcoming = Reminder.objects.select_related('patient').filter(scheduled_time__gte=now)
    overdue = Reminder.objects.select_related('patient').filter(scheduled_time__lt=now)

    if query:
        upcoming = upcoming.filter(
            message__icontains=query
        ) | upcoming.filter(
            patient__full_name__icontains=query
        )
        overdue = overdue.filter(
            message__icontains=query
        ) | overdue.filter(
            patient__full_name__icontains=query
        )

    return render(request, 'nurse_panel/view_reminders.html', {
        'upcoming_reminders': upcoming.order_by('scheduled_time'),
        'overdue_reminders': overdue.order_by('-scheduled_time'),
        'query': query,
    })


@login_required
def nurse_task_list(request):
    tasks = NurseTask.objects.filter(nurse=request.user).order_by('due_time')
    return render(request, 'nurse_panel/task_list.html', {'tasks': tasks})


@login_required
def compose_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user)  # ← Pass sender!
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('nurse_panel:inbox')
    else:
        form = MessageForm(sender=request.user)
    
    return render(request, 'nurse_panel/compose.html', {'form': form})


@login_required
def message_inbox(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'nurse_panel/inbox.html', {'messages': messages})


@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content')
        receiver = User.objects.get(id=receiver_id)
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return redirect('nurse_panel:message_inbox')
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'nurse_panel/send_message.html', {'users': users})


@login_required
def nurse_dashboard(request):
    user = request.user
    if user.role != 'nurse':
        return render(request, '403.html')

    medication_orders = MedicationOrder.objects.all().order_by('-start_date')
    medication_logs = MedicationLog.objects.filter(administered_by=user)
    med_requests = MedicationRequest.objects.filter(nurse=user)

    return render(request, 'nurse_panel/dashboard.html', {
        'medication_orders': medication_orders,
        'medication_logs': medication_logs,
        'med_requests': med_requests,
    })

