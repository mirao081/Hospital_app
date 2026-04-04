from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Doctor, Appointment
<<<<<<< HEAD
from .models import Notification, MedicalRecord
from datetime import date
from core.models import Message
from .forms import MedicalRecordForm



=======
from .models import Notification, MedicalRecord,Interaction, DiagnosticTest,StaffMessage, ReferralRequest, PatientPortalRequest
# from .models import DoctorTask, DoctorReminder, OnCallSchedule, KnowledgeBaseEntry
from datetime import date,timedelta
from django.utils import timezone
from core.models import Message
from django.contrib import messages
from patient_panel.models import Medication
from .forms import MedicalRecordForm
from cashier.models import Alert
from core.models import Enquiry
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .models import AnalyticsConfig
from django.db.models import Q, Count, Sum
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf


@login_required
def doctor_dashboard(request):
    doctor = Doctor.objects.get(user=request.user)
<<<<<<< HEAD

    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    confirmed = Appointment.objects.filter(doctor=doctor, status='confirmed').count()
    pending = Appointment.objects.filter(doctor=doctor, status__iexact='pending').count()

=======
    now = timezone.now()
    user = doctor.user

    # --- Appointment stats ---
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    confirmed = Appointment.objects.filter(doctor=doctor, status__iexact='Confirmed').count()
    pending = Appointment.objects.filter(doctor=doctor, status__iexact='Pending').count()

    # --- Today / Upcoming ---
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    today_appointments = Appointment.objects.filter(
        doctor=doctor, datetime__date=date.today()
    ).order_by('datetime')

    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor, datetime__date__gt=date.today()
    ).order_by('datetime')

<<<<<<< HEAD
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
=======
    # --- Missed / Cancelled ---
    missed_cancelled = Appointment.objects.filter(
        doctor=doctor,
        status__in=['Missed', 'Cancelled'],
        datetime__date=date.today()
    ).order_by('-datetime')

    # --- Emergency / Walk-in ---
    emergency_cases = Appointment.objects.filter(
        doctor=doctor,
        appointment_type__in=['Emergency', 'Walk-in'],
        datetime__date=date.today()
    ).order_by('datetime')

    # --- Queue Tracker ---
    patient_queue = Appointment.objects.filter(
        doctor=doctor,
        status='Scheduled',
        datetime__gte=now
    ).order_by('datetime')

    # --- Notifications / Records / Messages ---
    notifications = Notification.objects.filter(doctor=doctor, read=False).order_by('-timestamp')[:5]
    recent_records = MedicalRecord.objects.filter(doctor=doctor).order_by('-date_created')[:5]
    messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')[:5]
    enquiries = Enquiry.objects.all().order_by('-created_at')[:5]

    # --- Pending tasks ---
    pending_lab_reviews = MedicalRecord.objects.filter(doctor=doctor, lab_results__isnull=True).count()
    pending_prescriptions = MedicalRecord.objects.filter(doctor=doctor, prescription__isnull=True).count()

    # --- Unread counts ---
    total_unread_count = (
        Message.objects.filter(recipient=request.user, is_read=False).count() +
        Enquiry.objects.filter(is_read=False).count()
    )

    # --- Clinical data ---
    recent_interactions = Interaction.objects.order_by('-date')[:5]
    critical_alerts = Alert.objects.filter(is_critical=True, is_resolved=False).order_by('-created_at')
    pending_tests = DiagnosticTest.objects.filter(status='pending').order_by('due_date')[:5]
    medications = Medication.objects.filter(patient__user=request.user).order_by('-prescribed_date')[:5]

    clinical_data = {
        "recent_interactions": recent_interactions,
        "critical_alerts": critical_alerts,
        "pending_tests": pending_tests,
        "medications": medications,
    }

    # --- Communication & Collaboration ---
    staff_messages = StaffMessage.objects.all().order_by('-created_at')[:5]

    # --- Referrals (safe query) ---
    referrals = ReferralRequest.objects.filter(
        Q(to_doctor=doctor) |
        Q(to_user=user) |
        Q(patient__doctor__isnull=False, patient__doctor=doctor)
    ).select_related("patient__user", "to_doctor__user", "to_user", "created_by").order_by("-created_at")[:5]

    def role_label(u):
        if not u:
            return ""
        return (getattr(u, "role", "") or "").replace("_", " ").title()

    referral_cards = []
    for r in referrals:
        # From staff
        from_staff = (
            f"{r.created_by.get_full_name()} ({r.created_by_role or role_label(r.created_by)})"
            if r.created_by else "Unknown"
        )

        # To staff
        if r.to_doctor and r.to_doctor.user:
            to_staff = f"Dr. {r.to_doctor.user.get_full_name()}"
        elif r.to_user:
            to_staff = f"{r.to_user.get_full_name()} ({role_label(r.to_user)})"
        else:
            to_staff = "Unassigned"

        # Patient name safely
        patient_name = r.patient.user.get_full_name() if r.patient and r.patient.user else "Unknown"

        referral_cards.append({
            "patient_name": patient_name,
            "from_staff": from_staff,
            "to_staff": to_staff,
            "status": r.status.title(),
            "reason": r.reason or "",
        })

    patient_requests = PatientPortalRequest.objects.filter(doctor=doctor).order_by('-created_at')[:5]

    # --- Analytics (safe computations) ---
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = start_of_day - timedelta(days=start_of_day.weekday())
    start_of_month = start_of_day.replace(day=1)

    analytics_stats = {
        "today": Appointment.objects.filter(doctor=doctor, datetime__date=date.today()).count(),
        "week": Appointment.objects.filter(doctor=doctor, datetime__gte=start_of_week).count(),
        "month": Appointment.objects.filter(doctor=doctor, datetime__gte=start_of_month).count(),
    }

    # Case mix
    case_qs = MedicalRecord.objects.filter(doctor=doctor).values("diagnosis").annotate(count=Count("id")).order_by("-count")[:12]
    total_cases = sum(c["count"] for c in case_qs) or 0
    case_mix = [{"diagnosis": c.get("diagnosis") or "Unknown", "count": c["count"], "pct": round((c["count"] / total_cases * 100) if total_cases else 0, 1)} for c in case_qs]

    # Outcomes
    outcomes = {}
    if "outcome" in [f.name for f in MedicalRecord._meta.get_fields()]:
        out_qs = MedicalRecord.objects.filter(doctor=doctor).values("outcome").annotate(count=Count("id")).order_by("-count")
        outcomes = {o["outcome"] or "Unknown": o["count"] for o in out_qs}

    # Follow-up rate
    follow_up_rate = None
    fields = [f.name for f in MedicalRecord._meta.get_fields()]
    if "follow_up_required" in fields and "follow_up_done" in fields:
        required = MedicalRecord.objects.filter(doctor=doctor, follow_up_required=True).count()
        completed = MedicalRecord.objects.filter(doctor=doctor, follow_up_required=True, follow_up_done=True).count()
        follow_up_rate = (completed / required * 100) if required else None

    # Revenue
    revenue_today = Appointment.objects.filter(doctor=doctor, datetime__date=date.today()).aggregate(total=Sum("payment_amount"))["total"] or 0
    revenue_week = Appointment.objects.filter(doctor=doctor, datetime__gte=start_of_week).aggregate(total=Sum("payment_amount"))["total"] or 0
    revenue_month = Appointment.objects.filter(doctor=doctor, datetime__gte=start_of_month).aggregate(total=Sum("payment_amount"))["total"] or 0
    revenue_total = Appointment.objects.filter(doctor=doctor).aggregate(total=Sum("payment_amount"))["total"] or 0

    analytics = {
        "stats": analytics_stats,
        "case_mix": case_mix,
        "outcomes": outcomes,
        "follow_up_rate": follow_up_rate,
        "revenue": {
            "today": float(revenue_today),
            "week": float(revenue_week),
            "month": float(revenue_month),
            "total": float(revenue_total),
        },
    }

    # # --- Doctor Productivity & Workflow ---
    # tasks = DoctorTask.objects.filter(doctor=doctor).order_by('-due_date')[:10]
    # reminders = DoctorReminder.objects.filter(doctor=doctor).order_by('-created_at')[:10]
    # oncall_shifts = OnCallSchedule.objects.filter(doctor=doctor).order_by('start_time')[:10]
    # knowledge_base = KnowledgeBaseEntry.objects.all().order_by('-updated_at')[:10]

    # --- Context ---
    context = {
        'stats': {'total_appointments': total_appointments, 'confirmed': confirmed, 'pending': pending},
        'todays_schedule': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'missed_cancelled': missed_cancelled,
        'emergency_cases': emergency_cases,
        'patient_queue': patient_queue,
        'notifications': notifications,
        'recent_records': recent_records,
        'messages': messages,
        'enquiries': enquiries,
        "staff_messages": staff_messages,
        "referrals": referrals,
        "referral_cards": referral_cards,
        "patient_requests": patient_requests,
        "analytics": analytics,
        # "doctor_tasks": tasks,
        "task_summary": {
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
            'reminders': notifications.count(),
            'lab_reviews': pending_lab_reviews,
            'prescriptions': pending_prescriptions,
            'messages': messages.count(),
<<<<<<< HEAD
        },
        'total_unread_count': total_unread_count
=======
            'enquiries': enquiries.count(),
        },
        # "reminders": reminders,
        # "oncall_shifts": oncall_shifts,
        # "knowledge_base": knowledge_base,
        'total_unread_count': total_unread_count,
        "clinical_data": clinical_data,
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    }

    return render(request, 'doctor_panel/dashboard.html', context)

<<<<<<< HEAD
=======
@login_required
def doctor_notifications(request):
    doctor = getattr(request.user, "doctor", None)
    if not doctor:
        return HttpResponse("Forbidden: You are not assigned as a doctor.", status=403)

    notifications = Notification.objects.filter(doctor=doctor).order_by('-timestamp')
    # Optionally mark as read
    if request.method == "POST":
        ids = request.POST.getlist("notification_ids")
        Notification.objects.filter(id__in=ids, doctor=doctor).update(read=True)
        return redirect("doctor_panel:doctor_notifications")

    return render(request, "doctor_panel/notifications.html", {"notifications": notifications})
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

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
<<<<<<< HEAD
=======
    # Only allow the recipient to view the message
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    message = get_object_or_404(Message, pk=pk, recipient=request.user)

    if not message.is_read:
        message.is_read = True
        message.save()

<<<<<<< HEAD
    return render(request, 'doctor_panel/message_detail.html', {
        'message': message
    })
=======
    return render(request, 'doctor_panel/message_detail.html', {'message': message})


@login_required
def view_record(request, pk):
    doctor = getattr(request.user, "doctor", None)
    appointment = get_object_or_404(Appointment, pk=pk)

    # ✅ Permission check
    if not doctor or appointment.doctor != doctor:
        return HttpResponse("Forbidden: You don’t have permission to view this record.", status=403)

    record = getattr(appointment, "medical_record", None)  # safe lookup

    return render(request, "doctor_panel/view_record.html", {
        "appointment": appointment,
        "record": record,
    })




login_required
def doctor_inbox(request):
    if not hasattr(request.user, 'doctor'):
        return HttpResponse("Unauthorized access.", status=403)

    # Mark unread messages as read
    Message.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    Enquiry.objects.filter(is_read=False).update(is_read=True)

    messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    enquiries = Enquiry.objects.all().order_by('-created_at')

    return render(request, 'doctor_panel/inbox.html', {
        'messages': messages,
        'enquiries': enquiries,
    })

@login_required
def mark_enquiry_read(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    enquiry.is_read = True
    enquiry.save()
    return redirect('admin_panel:inbox')  # or 'doctor_panel:inbox' depending on app

@login_required
def doctor_analytics(request):
    doctor = getattr(request.user, "doctor", None)
    if not doctor:
        return HttpResponse("Forbidden: You are not assigned as a doctor.", status=403)

    config = AnalyticsConfig.objects.order_by("-updated_at").first()
    return render(request, "doctor_panel/analytics.html", {"config": config})


@login_required
def doctor_analytics_data(request):
    doctor = getattr(request.user, "doctor", None)
    if not doctor:
        return JsonResponse({"error": "forbidden"}, status=403)

    now = timezone.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = start_of_day - timezone.timedelta(days=now.weekday())
    start_of_month = start_of_day.replace(day=1)

    # --- Patient statistics ---
    stats = {
        "today": Appointment.objects.filter(doctor=doctor, datetime__date=date.today()).count(),
        "week": Appointment.objects.filter(doctor=doctor, datetime__gte=start_of_week).count(),
        "month": Appointment.objects.filter(doctor=doctor, datetime__gte=start_of_month).count(),
    }

    # --- Case mix breakdown ---
    # Assuming MedicalRecord has `diagnosis` (CharField/TextField) linked to Appointment
    case_qs = (
        MedicalRecord.objects.filter(doctor=doctor)
        .values("diagnosis")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )
    total_cases = sum([c["count"] for c in case_qs]) or 1
    case_mix = [
        {"diagnosis": c["diagnosis"], "count": c["count"], "pct": round((c["count"] / total_cases) * 100, 1)}
        for c in case_qs
    ]

    # --- Outcomes / Follow-up ---
    # Assuming MedicalRecord has `outcome` and `follow_up_required` / `follow_up_done`
    outcomes = {}
    follow_up_rate = None
    if hasattr(MedicalRecord, "outcome"):
        outcome_qs = (
            MedicalRecord.objects.filter(doctor=doctor)
            .values("outcome")
            .annotate(count=Count("id"))
        )
        outcomes = {o["outcome"] or "Unknown": o["count"] for o in outcome_qs}

    if hasattr(MedicalRecord, "follow_up_required") and hasattr(MedicalRecord, "follow_up_done"):
        required = MedicalRecord.objects.filter(doctor=doctor, follow_up_required=True).count()
        completed = MedicalRecord.objects.filter(doctor=doctor, follow_up_required=True, follow_up_done=True).count()
        follow_up_rate = (completed / required) if required > 0 else None

    # --- Revenue contribution ---
    # Assuming Appointment has `billing_amount` (DecimalField/FloatField)
    revenue = Appointment.objects.filter(doctor=doctor).aggregate(total=Sum("billing_amount"))
    revenue_total = float(revenue["total"] or 0)

    return JsonResponse(
        {
            "stats": stats,
            "case_mix": case_mix,
            "outcomes": outcomes,
            "follow_up_rate": follow_up_rate,
            "revenue": revenue_total,
        }
    )


@login_required
@require_POST
def update_request_status(request, pk):
    """
    Handles doctor actions on a PatientPortalRequest.
    Actions supported via form button named 'action':
      - schedule  => create Appointment (teleconsultation) and set request to 'in_progress'
      - in_progress => set request.status = 'in_progress'
      - resolved => set request.status = 'resolved'
    If scheduling, optional 'schedule_datetime' (HTML datetime-local) can be sent; otherwise schedule next day 09:00.
    """
    req = get_object_or_404(PatientPortalRequest, id=pk)

    # Permission: only the assigned doctor may update the request
    if req.doctor.user != request.user:
        return HttpResponse("Forbidden", status=403)

    action = request.POST.get("action")
    schedule_str = request.POST.get("schedule_datetime", "").strip()

    # normalize action
    if action not in ("schedule", "in_progress", "resolved"):
        # invalid action -> redirect back
        return redirect("doctor_panel:doctor_dashboard")

    # If scheduling requested and this is a teleconsultation, create an Appointment
    if action == "schedule" and req.request_type == "teleconsultation":
        # parse schedule datetime if provided
        scheduled_dt = None
        if schedule_str:
            dt = parse_datetime(schedule_str)
            if dt:
                if timezone.is_naive(dt):
                    # treat the datetime-local as local => make it aware in current timezone
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
                scheduled_dt = dt

        # fallback default: next day at 09:00 local time
        if scheduled_dt is None:
            dt = timezone.now() + timedelta(days=1)
            # set to 09:00 next day (local)
            scheduled_dt = dt.replace(hour=9, minute=0, second=0, microsecond=0)

        # Build Appointment object (map fields generically; adapt if your Appointment model differs)
        appt = Appointment()
        appt.doctor = req.doctor
        # if request links to a Patient object, set it; otherwise set name/phone/email fields if present
        if getattr(req, "patient", None):
            appt.patient = req.patient
        else:
            # some Appointment models accept full_name/email/phone — set if available
            if hasattr(appt, "full_name"):
                appt.full_name = req.patient_name
            if hasattr(appt, "phone"):
                appt.phone = req.patient_contact or ""
            if hasattr(appt, "email"):
                appt.email = ""  # optionally store if you collect email in request

        # datetime field
        if hasattr(appt, "datetime"):
            appt.datetime = scheduled_dt

        # mark appointment type and status where applicable
        if hasattr(appt, "appointment_type"):
            # try to use same token used elsewhere in your app (adjust string if your choices use lowercase)
            appt.appointment_type = "Teleconsultation"
        if hasattr(appt, "status"):
            # choose 'Scheduled' as default; adjust if you use other statuses
            appt.status = "Scheduled"

        # set a reason/comment if Appointment model supports it
        if hasattr(appt, "reason"):
            appt.reason = req.message[:2000]  # trim if needed
        if hasattr(appt, "comment"):
            appt.comment = f"Auto-created from portal request #{req.id}"

        # Save appointment
        appt.save()

        # update request status
        req.status = "in_progress"
        req.save()

        # redirect back to dashboard (or to the appointment detail if you prefer)
        return redirect("doctor_panel:doctor_dashboard")

    # Non-schedule actions: just update status
    if action in ("in_progress", "resolved"):
        req.status = action
        req.save()
        return redirect("doctor_panel:doctor_dashboard")

    # fallback
    return redirect("doctor_panel:doctor_dashboard")

def update_request(request, pk):
    req = get_object_or_404(PatientPortalRequest, id=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        schedule_datetime = request.POST.get("schedule_datetime")

        if action == "schedule" and schedule_datetime:
            req.status = "scheduled"
            req.scheduled_datetime = schedule_datetime
        elif action == "in_progress":
            req.status = "in_progress"
        elif action == "resolved":
            req.status = "resolved"

        req.save()

    # Redirect back to the same page and scroll to section
    return redirect(f"{request.META.get('HTTP_REFERER')}#portal-requests")
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
