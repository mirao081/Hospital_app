from cashier.models import AuditLog
from django.db.models import Count
from .models import Patient

def log_audit_action(user, action, model, object_id=None, description=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        model=model,
        object_id=object_id,
        description=description
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

def get_staff_role(user):
    if hasattr(user, "doctor"):
        return "doctor"
    if hasattr(user, "nurse"):
        return "nurse"
    if hasattr(user, "pharmacist"):
        return "pharmacist"
    if hasattr(user, "labtechnician"):
        return "lab"
    if user.is_superuser or user.is_staff:
        return "admin"
    return "user"

def get_referral_summary():
    referral_data = (
        Patient.objects.values("referral_source")
        .annotate(count=Count("id"))
        .order_by()
    )
    REFERRAL_LABELS = dict(Patient.REFERRAL_CHOICES)

    return [
        {
            "label": REFERRAL_LABELS.get(item["referral_source"], "Unknown"),
            "count": item["count"],
        }
        for item in referral_data
    ]
