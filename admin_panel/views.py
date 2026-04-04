# Standard library imports
import json
from datetime import date, datetime, timedelta, time as time_obj
from itertools import chain
from django.core.paginator import Paginator
# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.timezone import now, localdate, localtime
from django.db.models import Q, F, Sum, Count,DecimalField
from django.db.models.functions import TruncDay, TruncMonth, TruncYear,TruncDate
from django.db.models.functions import Cast
from django.db.models import IntegerField
<<<<<<< HEAD


=======
from core.models import AccessLog, FailedLoginAttempt
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
# App-specific imports
from core.decorators import admin_required
from core.forms import MessageForm, SignUpForm
from .forms import AdminRegisterForm
from core.models import (
    Doctor, Department, Patient, Appointment, InventoryItem, Room, Bed,
    ActivityLog, Attendance, StaffProfile, StaffAttendance, Message, Enquiry,
<<<<<<< HEAD
    User, RefundRequest
=======
    User, RefundRequest,PatientNote
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
)
from cashier.models import Payment,Invoice
from pharmacist_panel.models import Medicine
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponse
from django.db.models import ExpressionWrapper, DurationField, Avg
from patient_panel.models import Visit
from core.models import Admission
<<<<<<< HEAD
from .models import RevenueAging, CostPerPatient, InsuranceClaim, CashFlowForecast,KPITracking,ClinicalMetric,ClinicalMetric
from receptionist_panel.forms import PatientForm
from .forms import ClinicalMetricForm
from core.models import SurveyResponse, AppointmentReminder, Feedback
from collections import defaultdict
from datetime import timedelta

=======
from .models import RevenueAging, CostPerPatient, InsuranceClaim, CashFlowForecast,KPITracking,ClinicalMetric,ClinicalMetric,PaymentModeReport
from receptionist_panel.forms import PatientForm
from .forms import ClinicalMetricForm
from core.models import SurveyResponse, AppointmentReminder, Feedback
# ✅ CORRECT
from admin_panel.utils.metrics import get_kpi_data
from admin_panel.utils.metrics import get_revenue_by_service_type 
from .utils.metrics import get_total_revenue
from core.models import InventoryItem
from admin_panel.models import AutomationLog
from django.db.models import Sum, Value,DecimalField
from django.db.models.functions import Coalesce
from cashier.models import Refund
from itertools import chain
from django.http import Http404
from doctor_panel.utils import get_comm_context
from core.utils import get_referral_summary 
from core.utils import get_staff_role
from doctor_panel.models import StaffMessage, PatientPortalRequest,ReferralRequest
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf





# Custom user model
User = get_user_model()


@login_required
def admin_dashboard(request):
    today = localdate()
    current_time = now()
    current_year = today.year
<<<<<<< HEAD
=======
 
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

    # Inventory & Medicine Alerts
    inventory_alerts = InventoryItem.objects.filter(quantity__lt=F('threshold'))
    medicine_alerts = Medicine.objects.filter(
        Q(stock__lte=5) | Q(expiry_date__lte=today + timedelta(days=7))
    ).distinct()

    combined_alerts = list(chain(
        [
            {
                "name": item.name,
                "category": item.category,
                "quantity": item.quantity,
                "threshold": item.threshold,
                "last_updated": item.updated_at,
                "type": "Inventory",
                "expiry_date": None,
            } for item in inventory_alerts
        ],
        [
            {
                "name": med.name,
                "category": "Medicine",
                "quantity": med.stock,
                "threshold": 5,
                "last_updated": getattr(med, 'updated_at', None),
                "type": "Medicine",
                "expiry_date": med.expiry_date,
            } for med in medicine_alerts
        ]
    ))

<<<<<<< HEAD
    attendance_today = {
        a.staff.id: a for a in Attendance.objects
        .annotate(day=TruncDate('date'))
        .filter(day=today)
        .select_related('staff__user')
    }

    staff_list = StaffProfile.objects.select_related('user').filter(user__is_active=True)
    staff_attendance = [{'staff': staff, 'attendance': attendance_today.get(staff.id)} for staff in staff_list]
=======
    # Get all attendance records and filter in Python
    attendance_qs = Attendance.objects.select_related('staff__user')
    attendance_today = {
        a.staff.id: a for a in attendance_qs if a.date == today
    }

    # Get all active staff
    staff_list = StaffProfile.objects.select_related('user').filter(user__is_active=True)

    # Match attendance with staff
    staff_attendance = [
        {'staff': staff, 'attendance': attendance_today.get(staff.id)}
        for staff in staff_list
    ]
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

    try:
        staff = StaffProfile.objects.get(user=request.user)
        user_attendance = Attendance.objects.filter(staff=staff, date=today).first()
    except StaffProfile.DoesNotExist:
        user_attendance = None

    # Stats
    total_patients = Patient.objects.count()
<<<<<<< HEAD
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()
    appointments_today = Appointment.objects.filter(datetime__date=today).count()
    total_revenue = Appointment.objects.aggregate(Sum('payment_amount'))['payment_amount__sum'] or 0
    admin_name = request.user.first_name or request.user.username

    # Logs & Messages
    activity_logs = ActivityLog.objects.order_by('-timestamp')[:20]
    pending_payments = Appointment.objects.filter(payment_status="Pending")
    recent_payments = Payment.objects.all().order_by('-date_received')[:10]
    refunds = RefundRequest.objects.select_related('payment', 'issued_by').order_by('-created_at')
=======
    revenue_summary = get_revenue_by_service_type()

    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()
    appointments_today = Appointment.objects.filter(datetime__date=today).count()
    payment = Payment.objects.order_by('-date_received').first()  # Or whatever selection logic you need


    total_revenue = (
        Coalesce(Sum('amount'), Value(0, output_field=DecimalField())) +
        Coalesce(Sum('payment_amount'), Value(0, output_field=DecimalField()))
)

    admin_name = request.user.first_name or request.user.username

    recent_access_logs = AccessLog.objects.select_related('user').order_by('-timestamp')[:10]
    recent_failed_logins = FailedLoginAttempt.objects.order_by('-timestamp')[:10]

    # Logs & Messages
    activity_logs = ActivityLog.objects.order_by('-timestamp')[:20]
    pending_payments = Appointment.objects.filter(
    payment_status="Pending",
    payment_amount__gt=0
)

    recent_payments = Payment.objects.all().order_by('-date_received')[:10]
    refunds = RefundRequest.objects.select_related('issued_by', 'payment').order_by('-created_at')


>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

    all_payments = Payment.objects.all()
    only_cashier_payment = all_payments.exists() and not all_payments.exclude(received_by=request.user).exists()
    total_pending_amount = pending_payments.aggregate(Sum('payment_amount'))['payment_amount__sum'] or 0

    unread_messages = Message.objects.filter(recipient=request.user, is_read=False).order_by('-sent_at')[:10]
    unread_count = unread_messages.count()
    recent_messages = unread_messages if unread_count else Message.objects.filter(recipient=request.user).order_by('-sent_at')[:5]
    messages_source = 'unread' if unread_count else 'recent'

<<<<<<< HEAD
    # Growth Stats
=======
    enquiries = Enquiry.objects.all().order_by('-created_at')

    # # Growth Stats
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)

    this_month_revenue = Appointment.objects.filter(datetime__date__gte=first_day_this_month).aggregate(
        total=Sum('payment_amount'))['total'] or 0
    last_month_revenue = Appointment.objects.filter(
        datetime__date__gte=first_day_last_month,
        datetime__date__lt=first_day_this_month).aggregate(
        total=Sum('payment_amount'))['total'] or 0
    revenue_growth = round(((this_month_revenue - last_month_revenue) / last_month_revenue) * 100, 2) if last_month_revenue > 0 else None

    missed_appointments = Appointment.objects.filter(status="Missed").count()
    no_show_rate = round((missed_appointments / total_appointments) * 100, 2) if total_appointments else 0

    new_patients_this_month = Patient.objects.filter(created_at__gte=first_day_this_month).count()
    new_patients_last_month = Patient.objects.filter(created_at__gte=first_day_last_month, created_at__lt=first_day_this_month).count()
    patient_growth = round(((new_patients_this_month - new_patients_last_month) / new_patients_last_month) * 100, 2) if new_patients_last_month > 0 else None

    doctor_count_for_util = User.objects.filter(role='doctor').count()
    appt_per_doctor = round(total_appointments / doctor_count_for_util, 2) if doctor_count_for_util > 0 else 0
<<<<<<< HEAD

=======
    
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    # Bed Stats
    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    available_beds = total_beds - occupied_beds
    occupancy_rate = (occupied_beds / total_beds) * 100 if total_beds else 0

    metrics = ClinicalMetric.objects.all().order_by('metric_type')

    # Averages (calculated in Python to avoid SQLite issues)
<<<<<<< HEAD
    visits = Visit.objects.exclude(check_in_time__isnull=True, seen_by_doctor_time__isnull=True)
    appointments = Appointment.objects.exclude(start_time__isnull=True, end_time__isnull=True)
    admissions = Admission.objects.exclude(check_in_time__isnull=True, bed_assigned_time__isnull=True, discharge_time__isnull=True)

    def compute_avg_duration(queryset, start_field, end_field):
        durations = []
        for item in queryset:
            start = getattr(item, start_field)
            end = getattr(item, end_field)
            if start and end:
                duration = (end - start).total_seconds() / 60  # in minutes
                durations.append(duration)
        return round(sum(durations) / len(durations), 2) if durations else 0

    avg_wait_time = compute_avg_duration(visits, 'check_in_time', 'seen_by_doctor_time')
    avg_appointment_duration = compute_avg_duration(appointments, 'start_time', 'end_time')
    avg_time_to_bed = compute_avg_duration(admissions, 'check_in_time', 'bed_assigned_time')
    avg_stay_duration = compute_avg_duration(admissions, 'bed_assigned_time', 'discharge_time')


   # Wait Time Trends (SQLite-safe version)
    # Safe way to calculate daily wait times in Python
    

    raw_visits = Visit.objects.exclude(
        check_in_time__isnull=True,
        seen_by_doctor_time__isnull=True
    )

    wait_times_by_day = defaultdict(list)

    for visit in raw_visits:
        day = visit.check_in_time.date()
        wait_duration = visit.seen_by_doctor_time - visit.check_in_time
        wait_minutes = wait_duration.total_seconds() / 60
        wait_times_by_day[day].append(wait_minutes)

    # Build chart data
    daily_wait_times = []
    for day in sorted(wait_times_by_day):
        daily_times = wait_times_by_day[day]
        avg_wait = sum(daily_times) / len(daily_times) if daily_times else 0
        daily_wait_times.append({
            'day': day.strftime('%Y-%m-%d'),
            'avg_wait': round(avg_wait, 2),
        })

    wait_time_chart_data = {
        "labels": [entry['day'] for entry in daily_wait_times],
        "data": [entry['avg_wait'] for entry in daily_wait_times],
    }


=======

# Helper function
    def compute_avg_duration(values_list):
        durations = []
        for start, end in values_list:
            if start and end:
                duration = (end - start).total_seconds() / 60  # duration in minutes
                durations.append(duration)
        return round(sum(durations) / len(durations), 2) if durations else 0

    # Visits: wait time
    visits = Visit.objects.exclude(
        check_in_time__isnull=True,
        seen_by_doctor_time__isnull=True
    ).values_list('check_in_time', 'seen_by_doctor_time')

    # Admissions: time to bed
    admissions_time_to_bed = Admission.objects.exclude(
        admitted_at__isnull=True,
        bed_assigned_at__isnull=True
    ).values_list('admitted_at', 'bed_assigned_at')

    # Admissions: stay duration
    admissions_stay_duration = Admission.objects.exclude(
        bed_assigned_at__isnull=True,
        discharged_at__isnull=True
    ).values_list('bed_assigned_at', 'discharged_at')

    # Appointments: fixed duration assumption (30 min)
    appointment_duration_minutes = 30
    appointment_count = Appointment.objects.filter(datetime__isnull=False).count()
    avg_appointment_duration = appointment_duration_minutes if appointment_count else 0

    # Calculate averages
    avg_wait_time = compute_avg_duration(visits)
    avg_time_to_bed = compute_avg_duration(admissions_time_to_bed)
    avg_stay_duration = compute_avg_duration(admissions_stay_duration)

    patients_qs = Patient.objects.select_related('user')
    patients_sorted = sorted(patients_qs, key=lambda p: p.full_name.lower())

    paginator = Paginator(patients_sorted, 5)  # 5 per page
    page_number = request.GET.get('page', 1)
    patients = paginator.get_page(page_number)

    # If AJAX request, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for p in patients:
            data.append({
                "id": p.id,
                "full_name": p.full_name,
                "notes_url": f"/dashboard/admin/patient/{p.id}/notes/"
            })
        return JsonResponse({
            "patients": data,
            "has_next": patients.has_next(),
            "has_prev": patients.has_previous(),
            "next_page": patients.next_page_number() if patients.has_next() else None,
            "prev_page": patients.previous_page_number() if patients.has_previous() else None
        })


   # Wait Time Trends (SQLite-safe version)
    daily_wait_times = Visit.objects.exclude(
        check_in_time__isnull=True,
        seen_by_doctor_time__isnull=True
    ).annotate(
        day=TruncDay('check_in_time'),
        wait=ExpressionWrapper(
            F('seen_by_doctor_time') - F('check_in_time'),
            output_field=DurationField()
        )
    ).values('day').annotate(
        avg_wait=Avg('wait')
    ).order_by('day')

    wait_time_chart_data = {
        "labels": [entry['day'].strftime('%Y-%m-%d') for entry in daily_wait_times],
        "data": [
            round(entry['avg_wait'].total_seconds() / 60, 2)
            if entry['avg_wait'] is not None else 0
            for entry in daily_wait_times
        ],
    }

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    # Room Data
    rooms = []
    for room in Room.objects.all():
        total = room.beds.count()
        occupied = room.beds.filter(is_occupied=True).count()
        available = total - occupied
        rate = round((occupied / total) * 100, 1) if total else 0
        rooms.append({
            'name': room.number,
            'total_beds': total,
            'occupied_beds': occupied,
            'available_beds': available,
            'occupancy_rate': rate,
        })

    room_qs = Room.objects.prefetch_related('beds__patient__user').order_by('number')

    room_paginator = Paginator(room_qs, 1)
    room_page_number = request.GET.get('room_page')
    room_page = room_paginator.get_page(room_page_number)
    selected_room = room_page.object_list[0] if room_page.object_list else None
    beds = selected_room.beds.all().select_related('room', 'patient__user') if selected_room else []

<<<<<<< HEAD
    # KPI
    kpi_items = KPITracking.objects.all()
    from .utils import get_kpi_data  # Make sure you have this
=======
    recent_notes = PatientNote.objects.select_related('patient', 'created_by').order_by('-created_at')[:10]
    # KPI
    
    kpi_items = KPITracking.objects.all()
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    kpi_data = get_kpi_data()
    kpi_map = {item['feature']: item['value'] for item in kpi_data}

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("admin/partials/room_section.html", context, request=request)
        return HttpResponse(html)

<<<<<<< HEAD
    def serialize(queryset, date_field, value_field):
        return {
            "labels": [
                entry[date_field].strftime('%Y-%m-%d') if 'day' in date_field
                else entry[date_field].strftime('%B %Y') if 'month' in date_field
                else str(entry[date_field].year)
                for entry in queryset
            ],
            "data": [float(entry[value_field] or 0) for entry in queryset]
        }
=======
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

    daily_appointments = Appointment.objects.filter(datetime__year=current_year).annotate(
        day=TruncDay('datetime')).values('day').annotate(count=Count('id')).order_by('day')

    monthly_appointments = Appointment.objects.filter(datetime__year=current_year).annotate(
        month=TruncMonth('datetime')).values('month').annotate(count=Count('id')).order_by('month')

    yearly_appointments = Appointment.objects.annotate(
        year=TruncYear('datetime')).values('year').annotate(count=Count('id')).order_by('year')

    daily_income = Payment.objects.filter(
        date_received__year=current_year
    ).annotate(
        day=TruncDay('date_received')
    ).values('day').annotate(
        total=Sum('amount')
    ).order_by('day')

    monthly_income = Appointment.objects.filter(datetime__year=current_year).annotate(
        month=TruncMonth('datetime')).values('month').annotate(total=Sum('payment_amount')).order_by('month')

    yearly_income = Appointment.objects.annotate(
        year=TruncYear('datetime')).values('year').annotate(total=Sum('payment_amount')).order_by('year')
<<<<<<< HEAD

=======
    def serialize(queryset, date_field, value_field):
        return {
            "labels": [
                entry[date_field].strftime('%Y-%m-%d') if 'day' in date_field
                else entry[date_field].strftime('%B %Y') if 'month' in date_field
                else str(entry[date_field].year)
                for entry in queryset
            ],
            "data": [float(entry[value_field] or 0) for entry in queryset]
        }
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    total_surveys = SurveyResponse.objects.count()
    total_reminders = AppointmentReminder.objects.count()
    total_feedback = Feedback.objects.count()

    upcoming_appointments = Appointment.objects.select_related('doctor', 'doctor__user').filter(datetime__gt=current_time).order_by('datetime')[:10]

    users = User.objects.all().order_by('-date_joined')
    revenue_data = RevenueAging.objects.all().order_by('due_date')

    cost_entry = CostPerPatient.objects.order_by('-date').first()
    cost_summary = {
        "date": cost_entry.date if cost_entry else "N/A",
        "cost_per_visit": cost_entry.cost_per_visit() if cost_entry else 0,
    }

    claims = InsuranceClaim.objects.all()
    claim_stats = {
        "submitted": claims.filter(status='submitted').count(),
        "approved": claims.filter(status='approved').count(),
        "rejected": claims.filter(status='rejected').count(),
        "total_claimed": claims.aggregate(Sum('amount_claimed'))['amount_claimed__sum'] or 0
    }

    forecasts = CashFlowForecast.objects.annotate(
    net_cash=ExpressionWrapper(
        F('expected_income') - F('expected_expenses'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )
).order_by('forecast_month')

    total_cash_flow = forecasts.aggregate(
        total=Sum('net_cash')
    )['total'] or 0

<<<<<<< HEAD
    Patient.objects.filter(referral_source='').update(referral_source='other')
    referral_qs = Patient.objects.values('referral_source').annotate(count=Count('referral_source')).order_by('-count')
    referral_choices_dict = dict(Patient.REFERRAL_CHOICES)
    referral_summary = [{
        'label': referral_choices_dict.get(entry['referral_source'], 'Unknown'),
        'count': entry['count'],
    } for entry in referral_qs]

    context = {
        'form': SignUpForm(),
=======

    user_role = get_staff_role(request.user)

    if user_role == "admin":
        referrals = ReferralRequest.objects.select_related(
            'patient__user', 'created_by', 'to_doctor', 'to_user'
        ).all()
    else:
        referrals = ReferralRequest.objects.filter(created_by=request.user).select_related(
            'patient__user', 'created_by'
        )

    staff_messages = StaffMessage.objects.all().order_by('-created_at')[:5]
    patient_requests = PatientPortalRequest.objects.all().order_by('-created_at')[:5]  # fixed model name

   

    referral_list = []

    for ref in referrals:
        # Patient full name
        patient_name = ref.patient.user.get_full_name() if ref.patient else "Unknown"

        # Who referred
        if ref.from_doctor:
            from_staff = ref.from_doctor.user.get_full_name()
        elif ref.created_by:
            # fallback: just use the user who created the referral
            from_staff = ref.created_by.get_full_name()
        else:
            from_staff = "Unknown"

        referral_list.append({
            'patient_name': patient_name,
            'from_staff': from_staff,
            'status': ref.status.title(),
            'reason': ref.reason or "Referred during registration"
        })



    context = {
        'form': SignUpForm(),
        'referrals': referral_list,
        "role": user_role,
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        'staff_attendance': staff_attendance,
        'user_attendance': user_attendance,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'appointments_today': appointments_today,
<<<<<<< HEAD
        'total_revenue': total_revenue,
=======
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        'daily_appt_json': json.dumps(serialize(daily_appointments, 'day', 'count')),
        'monthly_appt_json': json.dumps(serialize(monthly_appointments, 'month', 'count')),
        'yearly_appt_json': json.dumps(serialize(yearly_appointments, 'year', 'count')),
        'daily_income_json': json.dumps(serialize(daily_income, 'day', 'total')),
        'monthly_income_json': json.dumps(serialize(monthly_income, 'month', 'total')),
        'yearly_income_json': json.dumps(serialize(yearly_income, 'year', 'total')),
        'total_nurses': User.objects.filter(role='nurse').count(),
        'total_pharmacists': User.objects.filter(role='pharmacist').count(),
        'total_lab_technicians': User.objects.filter(role='labtech').count(),
        'total_cashiers': User.objects.filter(role='cashier').count(),
        'total_receptionists': User.objects.filter(role='receptionist').count(),
        'rooms': rooms,
        'rooms_json': json.dumps(rooms),
        'wait_time_chart_data': wait_time_chart_data,
        'users': users,
        'current_year': current_year,
        'activity_logs': activity_logs,
        'upcoming_appointments': upcoming_appointments,
        'pending_payments': pending_payments,
<<<<<<< HEAD
=======
        'recent_payments': recent_payments,
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        'total_pending_amount': total_pending_amount,
        'unread_messages': recent_messages,
        'unread_count': unread_count,
        'messages_source': messages_source,
        'revenue_growth': revenue_growth,
        'no_show_rate': no_show_rate,
        'patient_growth': patient_growth,
        'appt_per_doctor': appt_per_doctor,
        'this_month_revenue': this_month_revenue,
        'recent_payments': recent_payments,
        'only_cashier_payment': only_cashier_payment,
<<<<<<< HEAD
        'refunds': refunds,
=======
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        'admin_name': admin_name,
        'combined_alerts': combined_alerts,
        'staff_list': staff_list,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'occupancy_rate': occupancy_rate,
        'room_page': room_page,
        'selected_room': selected_room,
        'beds': beds,
        'avg_wait_time': avg_wait_time,
        'avg_appointment_duration': avg_appointment_duration,
        'avg_time_to_bed': avg_time_to_bed,
        'avg_stay_duration': avg_stay_duration,
        "revenue_data": revenue_data,
        "cost_summary": cost_summary,
        "claim_stats": claim_stats,
        "forecasts": forecasts,
<<<<<<< HEAD
=======
        'revenue_summary': revenue_summary,
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        "total_cash_flow": total_cash_flow,
        'kpi_items': kpi_items,
        'live_kpi': kpi_data,
        'doctor_utilization': kpi_map.get("Doctor Utilization Rate", "N/A"),
        'staff_patient_ratio': kpi_map.get("Staff-to-Patient Ratio", "N/A"),
<<<<<<< HEAD
        'revenue_summary': kpi_map.get("Revenue by Service Type", "N/A"),
        'referral_summary': referral_summary,
=======
     
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        'metrics': metrics,
        'total_surveys': total_surveys,
        'total_reminders': total_reminders,
        'total_feedback': total_feedback,
<<<<<<< HEAD
    }
=======
        'recent_access_logs': recent_access_logs,
        'recent_failed_logins': recent_failed_logins,
        'total_revenue' : get_total_revenue,
        'payment': payment,
        'refunds': refunds,
        "patients": patients,
        "recent_notes": recent_notes,
        "enquiries": enquiries, 
        "referral_summary": get_referral_summary(),  # ✅ now from utils
        "referrals": referrals,
        "staff_messages": staff_messages,
        "patient_requests": patient_requests,

        
       
    }
    # ✅ Automation stats
    overdue_count = Invoice.objects.filter(is_flagged=True).count()
    low_inventory_count = InventoryItem.objects.filter(quantity__lte=10).count()
    last_run = AutomationLog.objects.order_by('-timestamp').first()

    context["automation_stats"] = {
        "overdue_count": overdue_count,
        "low_inventory_count": low_inventory_count,
        "last_run": last_run.timestamp if last_run else None
    }
    context.update(get_comm_context(request.user, scope="all", limit=5))
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

    return render(request, 'admin_panel/dashboard.html', context)

@admin_required
def register_user(request):
    role = request.GET.get('role') or request.POST.get('role')

    if request.method == 'POST':
<<<<<<< HEAD
        print("📍 Raw POST data:", request.POST)

=======
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        user_form = AdminRegisterForm(request.POST)
        patient_form = PatientForm(request.POST) if role == 'patient' else None

        if user_form.is_valid() and (patient_form is None or patient_form.is_valid()):
            username = user_form.cleaned_data['username']
<<<<<<< HEAD

            # Prevent duplicate usernames
=======
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
            if User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' already exists.")
                return redirect(f"{request.path}?role={role}")

<<<<<<< HEAD
            # Create user
=======
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
            user = user_form.save(commit=False)
            user.role = role
            user.save()

<<<<<<< HEAD
            if role == 'patient':
                # ✅ Safe to access cleaned_data here
                print("🎯 Referral selected:", patient_form.cleaned_data.get('referral_source'))

=======
            # ---------- patient flow ----------
            if role == 'patient':
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
                if Patient.objects.filter(user=user).exists():
                    messages.error(request, f"User '{username}' already has a patient profile.")
                    return redirect(f"{request.path}?role=patient")

                patient = patient_form.save(commit=False)
                patient.user = user
<<<<<<< HEAD

                # Defensive referral source cleaning and fallback
                referral = patient_form.cleaned_data.get('referral_source', '').strip().lower()
                valid_choices = [choice[0] for choice in Patient.REFERRAL_CHOICES]
                if referral in valid_choices:
                    patient.referral_source = referral
                else:
                    print(f"⚠️ Invalid referral value received: {referral}")
                    patient.referral_source = 'other'

                patient.save()

                print("📌 Saved Patient instance:")
                print(f"  age: {patient.age}")
                print(f"  referral_source (raw): {patient.referral_source}")
                print(f"  referral_source (label): {patient.get_referral_source_display()}")
=======
                patient.referral_source = patient_form.cleaned_data.get('referral_source')
                patient.referred_by = patient_form.cleaned_data.get('referred_by')
                patient.referral_details = patient_form.cleaned_data.get('referral_details', '') or ''
                patient.registered_by = request.user

                referred_user = patient.referred_by
                if referred_user and referred_user.role == 'doctor':
                    patient.doctor = Doctor.objects.filter(user=referred_user).first()

                patient.save()

                # ---------- create ReferralRequest ----------
                if referred_user:
                    to_doctor = None
                    to_nurse = None
                    to_pharmacist = None
                    to_lab = None

                    if referred_user.role == 'doctor':
                        to_doctor = Doctor.objects.filter(user=referred_user).first()
                    elif referred_user.role == 'nurse':
                        to_nurse = referred_user
                    elif referred_user.role == 'pharmacist':
                        to_pharmacist = referred_user
                    elif referred_user.role == 'labtech':
                        to_lab = referred_user

                    ReferralRequest.objects.create(
                        patient=patient,
                        created_by=referred_user,
                        created_by_role=referred_user.role,
                        to_doctor=to_doctor,
                        to_nurse=to_nurse,
                        to_pharmacist=to_pharmacist,
                        to_lab=to_lab,
                        reason=(patient.referral_details or f"Referred by {referred_user.get_full_name()} during registration"),
                        status="pending",
                    )
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

                messages.success(request, "Patient registered successfully!")
                return redirect(f"{request.path}?role=patient")

<<<<<<< HEAD
=======
            # ---------- doctor flow ----------
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
            elif role == 'doctor':
                dept_id = request.POST.get('department')
                if not dept_id:
                    messages.error(request, "Please select a department.")
                    return redirect(f"{request.path}?role=doctor")
<<<<<<< HEAD

                try:
                    department = Department.objects.get(id=dept_id)
                    Doctor.objects.create(user=user, department=department)
                    messages.success(request, "Doctor registered successfully!")
                    return redirect(f"{request.path}?role=doctor")
                except Department.DoesNotExist:
                    messages.error(request, "Department does not exist.")
                    return redirect(f"{request.path}?role=doctor")

            # Default success
=======
                try:
                    department = Department.objects.get(id=dept_id)
                except Department.DoesNotExist:
                    messages.error(request, "Department does not exist.")
                    return redirect(f"{request.path}?role=doctor")
                Doctor.objects.create(user=user, department=department)
                messages.success(request, "Doctor registered successfully!")
                return redirect(f"{request.path}?role=doctor")

            # ---------- other roles ----------
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
            messages.success(request, "User registered successfully!")
            return redirect('admin_panel:admin_dashboard')

        else:
            messages.error(request, "There was a problem with the form.")
<<<<<<< HEAD
            print("User form errors:", user_form.errors)
            if patient_form:
=======
            if user_form.errors:
                print("User form errors:", user_form.errors)
            if patient_form and patient_form.errors:
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
                print("Patient form errors:", patient_form.errors)

    else:
        user_form = AdminRegisterForm()
        patient_form = PatientForm() if role == 'patient' else None

<<<<<<< HEAD
    departments = Department.objects.all()
=======
    # context for template
    departments = Department.objects.all()
    doctors = Doctor.objects.select_related('user').all()
    nurses = User.objects.filter(role='nurse').order_by('first_name', 'last_name')
    pharmacists = User.objects.filter(role='pharmacist').order_by('first_name', 'last_name')
    lab_techs = User.objects.filter(role='labtech').order_by('first_name', 'last_name')
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

    return render(request, 'admin_panel/register_user.html', {
        'form': user_form,
        'patient_form': patient_form,
        'departments': departments,
        'role': role,
<<<<<<< HEAD
=======
        'doctors': doctors,
        'nurses': nurses,
        'pharmacists': pharmacists,
        'lab_techs': lab_techs,
        'request': request,
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    })

@admin_required
def staff_checkin_checkout(request):
    user = request.user
    today = timezone.localdate()
    now = timezone.localtime()

    try:
        staff_profile = StaffProfile.objects.get(user=user)
    except StaffProfile.DoesNotExist:
        return redirect('admin_panel:admin_dashboard')  # or some fallback

    attendance, created = Attendance.objects.get_or_create(
        staff=staff_profile,
        date=today,
    )

    if attendance.check_in is None:
        attendance.check_in = now.time()
    elif attendance.check_out is None:
        attendance.check_out = now.time()

    attendance.save()
    return redirect('admin_panel:admin_dashboard')  # back to admin dashboard

@admin_required
def staff_toggle_attendance(request):
    if request.method == 'POST':
        try:
            staff = StaffProfile.objects.get(user=request.user)
        except StaffProfile.DoesNotExist:
            messages.error(request, "You do not have a Staff Profile. Please contact admin.")
            return redirect('admin_panel:admin_dashboard')

        today = timezone.localdate()
        now = timezone.localtime()

        attendance, created = Attendance.objects.get_or_create(staff=staff, date=today)

        if not attendance.check_in:
            attendance.check_in = now
            messages.success(request, "Checked in successfully!")
        elif not attendance.check_out:
            attendance.check_out = now
            messages.success(request, "Checked out successfully!")
        else:
            messages.info(request, "You have already checked out today.")

        attendance.save()

    return redirect('admin_panel:admin_dashboard')


def get_room_bed_stats():
    rooms_stats = []

    for room in Room.objects.all():
        total_beds = room.beds.count()
        occupied_beds = room.beds.filter(is_occupied=True).count()
        available_beds = total_beds - occupied_beds
        occupancy_rate = round((occupied_beds / total_beds) * 100, 1) if total_beds > 0 else 0

        rooms_stats.append({
            'name': room.number,  # or room.name depending on your model
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'available_beds': available_beds,
            'occupancy_rate': occupancy_rate
        })

    return rooms_stats


@admin_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.is_read = True
    message.save()
    return render(request, 'admin_panel/message_detail.html', {'message': message})


@admin_required
def mark_message_read(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.is_read = True
    message.save()
    return redirect('admin_panel:inbox')  # Use 'inbox' if your URL name is set correctly

<<<<<<< HEAD
=======

@login_required
def mark_enquiry_read(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    enquiry.is_read = True
    enquiry.save()
    return redirect('admin_panel:inbox')  # or 'doctor_panel:inbox' depending on app

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
@admin_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('admin_panel:inbox')  # or 'admin_dashboard' if you prefer
    else:
        form = MessageForm(sender=request.user)

    return render(request, 'admin_panel/send_message.html', {'form': form})

# for admin readonly payment view from the cashiers update


@login_required
def inbox_view(request):
    if not hasattr(request.user, 'doctor') and not request.user.is_staff:
        return HttpResponse("Unauthorized access.", status=403)

<<<<<<< HEAD
    Message.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    Enquiry.objects.filter(is_read=False).update(is_read=True)

    user_messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    all_enquiries = Enquiry.objects.all().order_by('-created_at') if request.user.is_staff else None
=======
    # Mark as read
    Message.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    Enquiry.objects.filter(is_read=False).update(is_read=True)

    # Messages for this doctor/admin
    user_messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')

    # Enquiries: show to both staff and doctors
    if request.user.is_staff:
        all_enquiries = Enquiry.objects.all().order_by('-created_at')
    else:
        all_enquiries = Enquiry.objects.all().order_by('-created_at')   # 👈 doctors get them too
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

    return render(request, 'admin_panel/inbox.html', {
        'messages': user_messages,
        'enquiries': all_enquiries,
    })

@admin_required
def message_detail_view(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    return render(request, 'admin_panel/message_detail.html', {'message': message})

# Corrected version using RefundRequest
def is_admin(user):
<<<<<<< HEAD
    return user.is_authenticated and user.role == 'Admin'

@login_required
def refund_approval_list(request):
    refunds = RefundRequest.objects.select_related('payment', 'issued_by').order_by('-created_at')
    return render(request, 'admin_panel/refund_approval_list.html', {'refunds': refunds})
=======
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def refund_approval_list(request):
    # Pending refund requests
    refund_requests = RefundRequest.objects.select_related('issued_by', 'payment').all()

    # Already approved refunds
    issued_refunds = Refund.objects.select_related('issued_by', 'payment').all()

    # Combine both QuerySets and sort by date (newest first)
    all_refunds = sorted(
        chain(refund_requests, issued_refunds),
        key=lambda x: x.created_at if hasattr(x, 'created_at') else x.issue_date,
        reverse=True
    )

    context = {
        'refunds': all_refunds,
    }
    return render(request, 'admin_panel/refund_approval_list.html', context)
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

@admin_required
def approve_refund(request, refund_id):
    refund = get_object_or_404(RefundRequest, id=refund_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        refund.admin_note = request.POST.get('admin_note', '')

        if action == 'approve':
            refund.approval_status = 'Approved'
            refund.approved_by = request.user
        elif action == 'reject':
            refund.approval_status = 'Rejected'
            refund.approved_by = request.user

        refund.save()
        return redirect('admin_panel:refund_approval_list')

    return render(request, 'admin_panel/approve_refund.html', {'refund': refund})

User = get_user_model()

@login_required
def check_in(request, user_id=None):
    if user_id:
        if not request.user.is_superuser:
            return HttpResponseForbidden("You are not allowed to check in others.")
        target_user = get_object_or_404(User, id=user_id)
    else:
        target_user = request.user

    staff = get_object_or_404(StaffProfile, user=target_user)
    today = localdate()

    if request.method == 'POST':
        attendance, _ = Attendance.objects.get_or_create(staff=staff, date=today)
        if not attendance.check_in:
            attendance.check_in = localtime().time()
            attendance.status = "Present"
            attendance.save()
            messages.success(request, f"{target_user.get_full_name()} has been checked in.")
        else:
            messages.info(request, f"{target_user.get_full_name()} has already checked in.")
        return redirect('admin_panel:admin_dashboard')

    return render(request, 'admin_panel/confirm_check_in.html', {'staff': staff})


@login_required
def check_out(request, user_id=None):
    if user_id:
        if not request.user.is_superuser:
            return HttpResponseForbidden("You are not allowed to check out others.")
        target_user = get_object_or_404(User, id=user_id)
    else:
        target_user = request.user

    staff = get_object_or_404(StaffProfile, user=target_user)
    today = localdate()

    if request.method == 'POST':
        attendance = Attendance.objects.filter(staff=staff, date=today).first()
        if attendance and not attendance.check_out:
            attendance.check_out = localtime().time()
            attendance.status = "Checked Out"
            attendance.save()
            messages.success(request, f"{target_user.get_full_name()} has been checked out.")
        else:
            messages.info(request, f"{target_user.get_full_name()} has already checked out.")
        return redirect('admin_panel:admin_dashboard')

    return render(request, 'admin_panel/confirm_check_out.html', {'staff': staff})


@require_POST
@login_required
def staff_manual_checkin(request):
    staff_id = request.POST.get("staff_id")
    action = request.POST.get("action")  # get selected action: checkin or checkout

    staff = get_object_or_404(StaffProfile, id=staff_id)
    today = localdate()

    attendance, _ = Attendance.objects.get_or_create(staff=staff, date=today)

    if action == "checkin":
        if not attendance.check_in:
            attendance.check_in = localtime().time()
            attendance.status = "Present"
            attendance.save()
            messages.success(request, f"{staff.user.get_full_name()} was checked in successfully.")
        else:
            messages.info(request, f"{staff.user.get_full_name()} is already checked in.")

    elif action == "checkout":
        if attendance.check_in and not attendance.check_out:
            attendance.check_out = localtime().time()
            attendance.status = "Checked Out"
            attendance.save()
            messages.success(request, f"{staff.user.get_full_name()} was checked out successfully.")
        elif not attendance.check_in:
            messages.warning(request, f"{staff.user.get_full_name()} hasn't checked in yet.")
        else:
            messages.info(request, f"{staff.user.get_full_name()} is already checked out.")

    else:
        messages.error(request, "Invalid action.")

    return redirect('admin_panel:admin_dashboard')


def financial_dashboard(request):
    # Revenue aging breakdown
    revenue_data = RevenueAging.objects.all().order_by('due_date')

    # Cost per patient visit (latest entry)
    cost_entry = CostPerPatient.objects.order_by('-date').first()
    cost_summary = {
        "date": cost_entry.date if cost_entry else None,
        "cost_per_visit": cost_entry.cost_per_visit() if cost_entry else 0,
    }

    # Insurance Claims Summary
    claims = InsuranceClaim.objects.all()
    claim_stats = {
        "submitted": claims.filter(status='submitted').count(),
        "approved": claims.filter(status='approved').count(),
        "rejected": claims.filter(status='rejected').count(),
        "total_claimed": claims.aggregate(Sum('amount_claimed'))['amount_claimed__sum'] or 0
    }

    # Cash Flow Forecast
    forecasts = CashFlowForecast.objects.all().order_by('forecast_month')
    total_cash_flow = sum([f.net_cash_flow() for f in forecasts])

    context = {
        "revenue_data": revenue_data,
        "cost_summary": cost_summary,
        "claim_stats": claim_stats,
        "forecasts": forecasts,
        "total_cash_flow": total_cash_flow,
    }
    return render(request, "admin_panel/dashboard.html", context)


<<<<<<< HEAD
def get_kpi_data():
    data = []

    # 1. Doctor Utilization Rate
    doctors = Doctor.objects.count()
    assumed_hours_per_day = 8
    total_available = doctors * assumed_hours_per_day

    today = date.today()
    booked = Appointment.objects.filter(date=today).count()
    utilization = round((booked / total_available) * 100, 2) if total_available else 0

    data.append({
        "feature": "Doctor Utilization Rate",
        "value": f"{utilization}%",
        "why": "Indicates how effectively doctors' time is being used"
    })

    # 2. Staff-to-Patient Ratio
    staff = StaffProfile.objects.count()
    patients = Patient.objects.count()
    ratio = f"1:{round(patients / staff)}" if staff > 0 else "N/A"

    data.append({
        "feature": "Staff-to-Patient Ratio",
        "value": ratio,
        "why": "Helps monitor understaffing or overstaffing"
    })

    # 3. Revenue by Service Type (including appointment revenue)
    service_revenue = Invoice.objects.values('service_type') \
        .annotate(total=Sum('total_due')).order_by('-total')

    appointment_revenue_qs = Appointment.objects.filter(
        payment_status='Confirmed',
        payment_amount__isnull=False
    )
    appointment_total = appointment_revenue_qs.aggregate(
        total=Sum('payment_amount')
    )['total'] or 0

    combined_services = list(service_revenue)
    combined_services.append({
        'service_type': 'appointments',
        'total': appointment_total
    })

    if combined_services:
        summary = ', '.join([
            f"{entry['service_type']}: ₦{entry['total']:,.2f}"
            for entry in combined_services
        ])
    else:
        summary = "No data"

    data.append({
        "feature": "Revenue by Service Type",
        "value": summary,
        "why": "Identifies high- and low-performing services"
    })

    # 4. Referral Source Tracking (corrected to show readable labels)
    if 'referral_source' in [field.name for field in Patient._meta.get_fields()]:
        referral_sources = Patient.objects.values('referral_source') \
            .annotate(count=Count('id')).order_by('-count')

        referral_dict = dict(Patient.REFERRAL_CHOICES)

        if referral_sources:
            ref_summary = ', '.join([
                f"{referral_dict.get(s['referral_source'], 'Unknown')}: {s['count']} (raw: '{s['referral_source']}')"
                for s in referral_sources
            ])
        else:
            ref_summary = "No data"
    else:
        ref_summary = "Field 'referral_source' not available"

    data.append({
        "feature": "Referral Source Tracking",
        "value": ref_summary,
        "why": "Understand how patients find your hospital"
    })

    return data

=======
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
@staff_member_required
def clinical_metrics_view(request):
    metrics = ClinicalMetric.objects.all().order_by('metric_type')

    if request.method == 'POST':
        metric_id = request.POST.get('metric_id')
        instance = ClinicalMetric.objects.get(id=metric_id)
        form = ClinicalMetricForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            messages.success(request, "Metric updated successfully.")
            return redirect('admin_panel:clinical_metrics')
        else:
            messages.error(request, "There was a problem updating the metric.")

    else:
        form = ClinicalMetricForm()

    return render(request, 'admin_panel/clinical_metrics.html', {
        'metrics': metrics,
        'form': form
    })

@staff_member_required
def patient_engagement_view(request):
    total_surveys = SurveyResponse.objects.count()
    total_reminders = AppointmentReminder.objects.count()
    total_feedback = Feedback.objects.count()

    return render(request, 'admin_panel/patient_engagement.html', {
        'total_surveys': total_surveys,
        'total_reminders': total_reminders,
        'total_feedback': total_feedback,
<<<<<<< HEAD
=======
    })

@login_required
@user_passes_test(is_admin)
def refund_approve(request, pk):
    refund = get_object_or_404(Refund, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")
        admin_note = request.POST.get("admin_note", "")
        refund.admin_note = admin_note

        if action == "approve":
            refund.is_approved = True
            refund.approved_by = request.user
        elif action == "reject":
            refund.is_approved = False
            refund.approved_by = request.user
        else:
            return render(request, "admin_panel/refund_approve.html", {"refund": refund, "error": "Invalid action"})

        refund.save()
        return redirect("admin_panel:refund_approval_list")  # ✅ fixed redirect

    return render(request, "admin_panel/refund_approve.html", {"refund": refund})

def refund_action(request, refund_id):
    refund = get_object_or_404(Refund, id=refund_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_note = request.POST.get('admin_note', '')

        # Save admin note
        refund.admin_note = admin_note

        if action == 'approve':
            refund.status = 'approved'
            refund.save()
            return redirect("admin_panel:refund_approval_list")  # ✅ fixed
        elif action == 'reject':
            refund.status = 'rejected'
            refund.save()
            return redirect("admin_panel:refund_approval_list")  # ✅ consistent

    return render(request, 'admin_panel/refund_approve.html', {'refund': refund})

def refund_list(request):
    refunds = Refund.objects.all()
    return render(request, 'admin_panel/refund_list.html', {'refunds': refunds})


@login_required
def patient_notes(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    notes = patient.notes.all()

    if request.method == "POST":
        note_text = request.POST.get("note")
        if note_text:
            PatientNote.objects.create(
                patient=patient,
                note=note_text,
                created_by=request.user
            )
            return redirect('admin_panel:patient_notes', patient_id=patient.id)

    return render(request, "admin_panel/patient_notes.html", {
        "patient": patient,
        "notes": notes
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    })