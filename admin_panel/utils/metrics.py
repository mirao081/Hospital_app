import math
<<<<<<< HEAD
from datetime import timedelta
from django.utils import timezone
from core.models import Admission
from admin_panel.models import ClinicalMetric, ClinicalComplication


def update_readmission_rate():
=======
import traceback
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Case, When, Value, CharField, F, DecimalField

from core.models import Admission, Appointment
from admin_panel.models import ClinicalMetric, ClinicalComplication, KPITracking
from cashier.models import Invoice, Payment
from admin_panel.models import RevenueAging  # ✅ Make sure this import points to the right app
from decimal import Decimal
from django.db.models.functions import Coalesce


def update_readmission_rate():
    """
    Calculates the 30-day hospital readmission rate and stores it in ClinicalMetric.
    """
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    now = timezone.now()
    one_month_ago = now - timedelta(days=30)

    try:
        discharges = Admission.objects.filter(
            discharged_at__isnull=False,
            discharged_at__gte=one_month_ago
        )
<<<<<<< HEAD
=======

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        readmitted_patients = 0

        for admission in discharges:
            patient = admission.patient
            readmissions = Admission.objects.filter(
                patient=patient,
                admitted_at__gt=admission.discharged_at
            ).exists()

            if readmissions:
                readmitted_patients += 1

        total_discharges = discharges.count()
        rate = (readmitted_patients / total_discharges * 100) if total_discharges else 0

        if math.isnan(rate) or math.isinf(rate):
            rate = 0

        ClinicalMetric.objects.update_or_create(
            metric_type='readmission',
            defaults={
                'description': 'Helps track quality of care',
                'value': f"{rate:.2f}%",
                'updated_at': now
            }
        )

    except Exception as e:
        print(f"⚠️ update_readmission_rate failed: {e}")
<<<<<<< HEAD


def update_outcome_trend():
=======
        traceback.print_exc()


def update_outcome_trend():
    """
    Calculates recovery outcome rate over the last 30 days and stores it in ClinicalMetric.
    """
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    now = timezone.now()
    one_month_ago = now - timedelta(days=30)

    try:
        recent_admissions = Admission.objects.filter(
            discharged_at__isnull=False,
            discharged_at__gte=one_month_ago
        )
<<<<<<< HEAD
=======

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        positive_outcomes = recent_admissions.filter(outcome__icontains='recovered').count()
        total = recent_admissions.count()

        rate = (positive_outcomes / total * 100) if total else 0

        if math.isnan(rate) or math.isinf(rate):
            rate = 0

        ClinicalMetric.objects.update_or_create(
            metric_type='outcomes',
            defaults={
                'description': 'Recovery rates, mortality rates, etc.',
                'value': f"{rate:.2f}% recovery rate",
                'updated_at': now
            }
        )

    except Exception as e:
        print(f"⚠️ update_outcome_trend failed: {e}")
<<<<<<< HEAD


def update_infection_rate():
=======
        traceback.print_exc()


def update_infection_rate():
    """
    Calculates clinical infection rate per 1000 patients and stores it in ClinicalMetric.
    """
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    now = timezone.now()
    one_month_ago = now - timedelta(days=30)

    try:
        total_admissions = Admission.objects.filter(admitted_at__gte=one_month_ago).count()
        total_complications = ClinicalComplication.objects.filter(reported_at__gte=one_month_ago).count()

        rate = (total_complications / total_admissions * 1000) if total_admissions else 0

        if math.isnan(rate) or math.isinf(rate):
            rate = 0

        ClinicalMetric.objects.update_or_create(
            metric_type='infection',
            defaults={
                'description': 'Clinical safety indicator',
                'value': f"{rate:.2f} per 1000 patients",
                'updated_at': now
            }
        )

    except Exception as e:
        print(f"⚠️ update_infection_rate failed: {e}")
<<<<<<< HEAD
=======
        traceback.print_exc()


# ✅ Add all service type label

SERVICE_LABELS = {
    'appointment': 'Appointment',
    'consultation': 'Consultation',
    'lab': 'Lab Test',
    'surgery': 'Surgery',
    'pharmacy': 'Pharmacy',
    'radiology': 'Radiology',
    'admission': 'Admission',
    'other': 'Other',
}

def get_revenue_by_service_type():
    try:
        combined = {}

        # Invoice revenue
        invoice_revenue = (
            Invoice.objects.values("service_type").annotate(total=Sum("total_due"))
        )
        for item in invoice_revenue:
            stype = item["service_type"]
            combined[stype] = combined.get(stype, 0) + float(item["total"] or 0)

        # Payment revenue
        payment_revenue = (
            Payment.objects.annotate(
                effective_service_type=Case(
                    When(appointment__isnull=False, then=Value("appointment")),
                    default=F("service_type"),
                    output_field=CharField(),
                )
            )
            .values("effective_service_type")
            .annotate(total=Sum("amount"))
        )
        for item in payment_revenue:
            stype = item["effective_service_type"]
            combined[stype] = combined.get(stype, 0) + float(item["total"] or 0)

        # Revenue aging
        aging_revenue = (
            RevenueAging.objects.values("service_type").annotate(total=Sum("amount_due"))
        )
        for item in aging_revenue:
            stype = item["service_type"]
            combined[stype] = combined.get(stype, 0) + float(item["total"] or 0)

        if not combined:
            return []

        # ✅ Return as a list of dicts
        summary = [
            {
                "label": SERVICE_LABELS.get(stype, stype.title()),
                "amount": f"₦{amount:,.2f}",
            }
            for stype, amount in combined.items()
        ]

        return summary

    except Exception as e:
        print(f"⚠️ Revenue by Service Type error: {e}")
        return []


def get_kpi_data():
    """
    Combines KPI data from the database and computed metrics.
    """
    data = []

    # Static KPIs
    for item in KPITracking.objects.all():
        data.append({
            'feature': item.feature,
            'value': getattr(item, 'value', 'N/A') or 'N/A',
            'why': item.importance
        })

    # Dynamic KPI: Revenue by Service Type
    data.append({
        'feature': 'Revenue by Service Type',
        'value': get_revenue_by_service_type(),   # <-- this returns a list of dicts now
        'why': 'Identifies high- and low-performing services'
    })

    return data


def get_total_revenue():
    """
    Returns only confirmed cash payments.
    """
    try:
        payment_total = Payment.objects.aggregate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        )['total'] or Decimal('0.00')

        return payment_total
    except Exception as e:
        print(f"⚠️ Total Revenue calculation error: {e}")
        return Decimal('0.00')
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
