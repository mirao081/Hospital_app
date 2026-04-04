import math
from datetime import timedelta
from django.utils import timezone
from core.models import Admission
from admin_panel.models import ClinicalMetric, ClinicalComplication


def update_readmission_rate():
    now = timezone.now()
    one_month_ago = now - timedelta(days=30)

    try:
        discharges = Admission.objects.filter(
            discharged_at__isnull=False,
            discharged_at__gte=one_month_ago
        )
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


def update_outcome_trend():
    now = timezone.now()
    one_month_ago = now - timedelta(days=30)

    try:
        recent_admissions = Admission.objects.filter(
            discharged_at__isnull=False,
            discharged_at__gte=one_month_ago
        )
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


def update_infection_rate():
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
