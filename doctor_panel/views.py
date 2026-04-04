from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Doctor, Appointment
from .models import Notification, MedicalRecord
from datetime import date
from core.models import Message
from .forms import MedicalRecordForm





@login_required
def doctor_dashboard(request):
    doctor = Doctor.objects.get(user=request.user)

    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    confirmed = Appointment.objects.filter(doctor=doctor, status='confirmed').count()
    pending = Appointment.objects.filter(doctor=doctor, status__iexact='pending').count()

    today_appointments = Appointment.objects.filter(
        doctor=doctor, datetime__date=date.today()
    ).order_by('datetime')

    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor, datetime__date__gt=date.today()
    ).order_by('datetime')

    notifications = Notification.objects.filter(doctor=doctor, read=False).order_by('-timestamp')[:5]
    recent_records = MedicalRecord.objects.filter(doctor=doctor).order_by('-date_created')[:5]
    messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')[:5]

    pending_lab_reviews = MedicalRecord.objects.filter(
        doctor=doctor, lab_results__isnull=True
    ).count()

    pending_prescriptions = MedicalRecord.objects.filter(
        doctor=doctor, prescription__isnull=True
    ).count()

    total_unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    context = {
        'stats': {
            'total_appointments': total_appointments,
            'confirmed': confirmed,
            'pending': pending,
        },
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'notifications': notifications,
        'recent_records': recent_records,
        'messages': messages,
        'tasks': {
            'reminders': notifications.count(),
            'lab_reviews': pending_lab_reviews,
            'prescriptions': pending_prescriptions,
            'messages': messages.count(),
        },
        'total_unread_count': total_unread_count
    }

    return render(request, 'doctor_panel/dashboard.html', context)


@login_required
def add_medical_record(request):
    doctor = Doctor.objects.get(user=request.user)

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.doctor = doctor
            record.save()
            return redirect('doctor_panel:doctor_dashboard')
    else:
        form = MedicalRecordForm()

    return render(request, 'doctor_panel/add_medical_record.html', {'form': form})


@login_required
def doctor_inbox_view(request):
    # Mark all messages as read for doctor
    Message.objects.filter(recipient=request.user, is_read=False).update(is_read=True)

    user_messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')

    return render(request, 'doctor_panel/inbox.html', {
        'messages': user_messages,
    })


@login_required
def message_detail_view(request, pk):
    message = get_object_or_404(Message, pk=pk, recipient=request.user)

    if not message.is_read:
        message.is_read = True
        message.save()

    return render(request, 'doctor_panel/message_detail.html', {
        'message': message
    })