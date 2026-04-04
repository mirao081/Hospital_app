from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PatientForm, AppointmentForm
from core.models import Appointment


@login_required
def receptionist_dashboard(request):
    return render(request, 'receptionist_panel/dashboard.html')



@login_required
def register_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('receptionist:receptionist_dashboard')
    else:
        form = PatientForm()
    return render(request, 'receptionist_panel/register_patient.html', {'form': form})

@login_required
def schedule_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('receptionist:receptionist_dashboard')
    else:
        form = AppointmentForm()
    return render(request, 'receptionist_panel/schedule_appointment.html', {'form': form})

@login_required
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-datetime')

    return render(request, 'receptionist_panel/appointment_list.html', {'appointments': appointments})


@login_required
def send_internal_message(request):
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        # TODO: Save or dispatch the message
        return render(request, 'receptionist_panel/message_sent.html', {
            'recipient': recipient,
            'subject': subject
        })
    return render(request, 'receptionist_panel/send_message.html')


@login_required
def patient_onboarding(request):
    return render(request, 'receptionist_panel/patient_onboarding.html')


@login_required
def service_guidelines(request):
    return render(request, 'receptionist_panel/service_guidelines.html')

