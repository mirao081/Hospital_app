from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils.timezone import localdate, localtime, now
from django.contrib.auth import get_user_model
from admin_panel.utils.session_logger import login_logger, logout_logger
from doctor_panel.models import Notification
from core.models import Appointment, FailedLoginAttempt, Patient, StaffProfile, Attendance, Admission, RefundRequest, Message
from cashier.models import Alert
from admin_panel.utils.metrics import update_readmission_rate, update_infection_rate, update_outcome_trend

User = get_user_model()

# -------------------------------
# Staff profile auto-create
# -------------------------------
@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if not created:
        return
    role = getattr(instance, 'role', None)
    if role in ['admin', 'nurse', 'pharmacist', 'labtech', 'receptionist', 'cashier']:
        if not hasattr(instance, 'staffprofile'):
            StaffProfile.objects.create(user=instance, role=role)

# -------------------------------
# Attendance logging
# -------------------------------
@receiver(user_logged_in)
def auto_check_in(sender, request, user, **kwargs):
    try:
        staff = StaffProfile.objects.get(user=user)
        today = localdate()
        attendance, _ = Attendance.objects.get_or_create(staff=staff, date=today)
        if not attendance.check_in:
            attendance.check_in = localtime().time()
            attendance.status = "Present"
            attendance.save()
    except StaffProfile.DoesNotExist:
        pass

@receiver(user_logged_out)
def auto_check_out(sender, request, user, **kwargs):
    try:
        staff = StaffProfile.objects.get(user=user)
        today = localdate()
        attendance = Attendance.objects.filter(staff=staff, date=today).first()
        if attendance and not attendance.check_out:
            attendance.check_out = localtime().time()
            attendance.save()
    except StaffProfile.DoesNotExist:
        pass

@receiver(user_logged_in)
def staff_logged_in_signal(sender, user, request, **kwargs):
    try:
        staff = StaffProfile.objects.get(user=user)
        Attendance.objects.get_or_create(staff=staff, date=localdate())
    except StaffProfile.DoesNotExist:
        pass

# -------------------------------
# Update metrics on patient discharge
# -------------------------------
@receiver(post_save, sender=Admission)
def update_metrics_on_discharge(sender, instance, **kwargs):
    if instance.discharged_at:
        print("📈 Patient discharged — updating clinical metrics...")
        try: update_readmission_rate()
        except Exception as e: print("⚠️ update_readmission_rate failed:", e)
        try: update_infection_rate()
        except Exception as e: print("⚠️ update_infection_rate failed:", e)
        try: update_outcome_trend()
        except Exception as e: print("⚠️ update_outcome_trend failed:", e)

# -------------------------------
# Failed login logging
# -------------------------------
@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
    FailedLoginAttempt.objects.create(
        username=credentials.get('username', 'Unknown'),
        ip_address=ip,
        user_agent=user_agent,
        timestamp=now()
    )

def get_client_ip(request):
    if request is None: return '0.0.0.0'
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

# -------------------------------
# Refund request alerts
# -------------------------------
@receiver(post_save, sender=RefundRequest)
def create_refund_alert(sender, instance, created, **kwargs):
    if created and instance.approval_status == 'Pending':
        print(f"Signal: Creating alert for NEW RefundRequest #{instance.id}")
        Alert.objects.create(
            alert_type='refund_approval',
            description=f"Refund request #{instance.id} for payment #{instance.payment.id} awaiting approval",
            is_resolved=False
        )
    elif not created and instance.approval_status == 'Pending':
        exists = Alert.objects.filter(
            alert_type='refund_approval',
            description__icontains=f"Refund request #{instance.id}",
            is_resolved=False
        ).exists()
        if not exists:
            Alert.objects.create(
                alert_type='refund_approval',
                description=f"Refund request #{instance.id} for payment #{instance.payment.id} awaiting approval",
                is_resolved=False
            )

@receiver(post_save, sender=RefundRequest)
def clear_refund_alert_on_approval(sender, instance, created, **kwargs):
    if not created and instance.approval_status in ['Approved', 'Rejected']:
        alerts = Alert.objects.filter(
            alert_type='refund_approval',
            is_resolved=False,
            description__icontains=f"Refund request #{instance.id}"
        )
        for alert in alerts:
            alert.is_resolved = True
            alert.save()

# -------------------------------
# Appointment notifications
# -------------------------------
@receiver(post_save, sender=Appointment)
def create_new_appointment_notification(sender, instance, created, **kwargs):
    if created:
        if instance.patient and instance.patient.user:
            patient_name = instance.patient.user.get_full_name()
        else:
            patient_name = "Unknown Patient"

        Notification.objects.create(
            doctor=instance.doctor,
            message=f"New appointment booked with {patient_name} at {instance.datetime}",
        )
        print(f"Signal fired: New appointment #{instance.id} notification created")
