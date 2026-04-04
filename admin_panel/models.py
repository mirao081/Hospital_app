from django.db import models
from django.utils import timezone
from core.models import Patient 
import uuid
from core.models import Admission 
from decimal import Decimal

class RevenueAging(models.Model):
    bill_reference = models.CharField(max_length=100, unique=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()

    def days_overdue(self):
        from django.utils import timezone
        return (timezone.now().date() - self.due_date).days

    def save(self, *args, **kwargs):
        if not self.bill_reference:
            self.bill_reference = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} - {self.bill_reference}"

class CostPerPatient(models.Model):
    date = models.DateField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_patients = models.PositiveIntegerField()

    def cost_per_visit(self):
        return self.total_cost / self.number_of_patients if self.number_of_patients else 0

    def __str__(self):
        return f"{self.date} - Cost per visit"


class InsuranceClaim(models.Model):
    CLAIM_STATUS = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    claim_id = models.CharField(max_length=100)
    patient_name = models.CharField(max_length=100)
    amount_claimed = models.DecimalField(max_digits=12, decimal_places=2)
    insurer = models.CharField(max_length=100)
    date_submitted = models.DateField()
    status = models.CharField(max_length=10, choices=CLAIM_STATUS)

    def __str__(self):
        return f"{self.claim_id} - {self.status}"


class CashFlowForecast(models.Model):
    forecast_month = models.DateField()

    # Ensure values are never None by setting default and null=False
    expected_income = models.DecimalField(
        max_digits=12, decimal_places=2, null=False, default=0
    )
    expected_expenses = models.DecimalField(
        max_digits=12, decimal_places=2, null=False, default=0
    )

    def net_cash_flow(self):
        # Defensive coding in case of legacy database rows or future edits
        income = self.expected_income or Decimal("0.00")
        expenses = self.expected_expenses or Decimal("0.00")
        return income - expenses

    def __str__(self):
        return f"Forecast - {self.forecast_month.strftime('%B %Y')}"
    
    
class KPITracking(models.Model):
    feature = models.CharField(max_length=100)
    importance = models.TextField(help_text="Explain why this feature matters.")

    def __str__(self):
        return self.feature
    

class ClinicalMetric(models.Model):
    METRIC_CHOICES = [
        ('readmission', 'Readmission Rates'),
        ('infection', 'Infection/Complication Rates'),
        ('outcomes', 'Treatment Outcome Trends'),
    ]

    metric_type = models.CharField(max_length=50, choices=METRIC_CHOICES, unique=True)
    description = models.TextField(help_text="Why this metric matters")
    value = models.CharField(max_length=100, help_text="Current metric value (e.g. 12%, 3 per 1000, etc.)")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value}"
    

class ClinicalComplication(models.Model):
    admission = models.ForeignKey(Admission, on_delete=models.CASCADE, related_name='complications')
    complication_type = models.CharField(max_length=100)
    from django.utils import timezone
    reported_at = models.DateTimeField(default=timezone.now)

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.complication_type} for {self.admission}"


# Financial & Billing Metrics 
