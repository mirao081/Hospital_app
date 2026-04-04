from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import localdate, localtime
from django.contrib.auth import get_user_model

from core.models import Patient, StaffProfile, Attendance, Admission
from admin_panel.utils.metrics import (
    update_readmission_rate,
    update_infection_rate,
    update_outcome_trend,
)

User = get_user_model()

# ✅ Create staff profile automatically when user is created
@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if not created:
        return

    role = getattr(instance, 'role', None)
    if role in ['admin', 'nurse', 'pharmacist', 'labtech', 'receptionist', 'cashier']:
        if not hasattr(instance, 'staffprofile'):
            StaffProfile.objects.create(user=instance, role=role)

# ✅ Automatically check in on login
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

# ✅ Automatically check out on logout
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

# ✅ Ensure attendance entry on login
@receiver(user_logged_in)
def staff_logged_in_signal(sender, user, request, **kwargs):
    try:
        staff = StaffProfile.objects.get(user=user)
        Attendance.objects.get_or_create(staff=staff, date=localdate())
    except StaffProfile.DoesNotExist:
        pass

# ✅ NEW: Auto-update clinical metrics when patient is discharged
@receiver(post_save, sender=Admission)
def update_metrics_on_discharge(sender, instance, **kwargs):
    if instance.discharged_at:
        print("📈 Patient discharged — updating clinical metrics...")

        try:
            update_readmission_rate()
        except Exception as e:
            print("⚠️ update_readmission_rate failed:", e)

        try:
            update_infection_rate()
        except Exception as e:
            print("⚠️ update_infection_rate failed:", e)

        try:
            update_outcome_trend()
        except Exception as e:
            print("⚠️ update_outcome_trend failed:", e)
