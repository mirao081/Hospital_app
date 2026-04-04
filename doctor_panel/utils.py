# doctor_panel/utils.py
from core.models import Message
from doctor_panel.models import ReferralRequest, PatientPortalRequest
from django.db.models import Q

def get_comm_context(user, scope="all", limit=5):
    """
    Build context for Communication & Collaboration section.
    Works for doctor, nurse, etc.
    """

    # Internal staff messages
    staff_messages = Message.objects.filter(
        recipient=user
    ).select_related("sender").order_by("-sent_at")[:limit]

    # Referrals: include only if user is doctor or nurse
    referrals = ReferralRequest.objects.none()
    if hasattr(user, "doctor"):
        referrals = ReferralRequest.objects.filter(
            Q(to_doctor=user.doctor) | Q(to_user=user)
        ).order_by("-created_at")[:limit]
    elif user.role == "nurse":
        referrals = ReferralRequest.objects.filter(
            Q(to_nurse=user) | Q(from_doctor__isnull=False)
        ).order_by("-created_at")[:limit]

    # Patient portal requests (only for doctors right now)
    patient_requests = PatientPortalRequest.objects.none()
    if hasattr(user, "doctor"):
        patient_requests = PatientPortalRequest.objects.filter(
            doctor=user.doctor
        ).order_by("-created_at")[:limit]

    return {
        "staff_messages": staff_messages,
        "referrals": referrals,
        "patient_requests": patient_requests,
    }

