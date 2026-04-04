from django.db import models
from django.utils import timezone
from core.models import Patient 
import uuid
from core.models import Admission 
from decimal import Decimal
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError

class RevenueAging(models.Model):
    SERVICE_CHOICES = [
        ("appointment", "Appointment"),
        ("consultation", "Consultation"),
        ("surgery", "Surgery"),
        ("pharmacy", "Pharmacy"),
        ("lab", "Lab Test"),
        ("admission", "Admission"),
        ("other", "Other"),
    ]

    bill_reference = models.CharField(max_length=100, unique=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES, default="other")   # 👈 NEW FIELD
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()

    def days_overdue(self):
        from django.utils import timezone
        return (timezone.now().date() - self.due_date).days

    def save(self, *args, **kwargs):
        import uuid
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
        try:
            if not self.number_of_patients:
                return 0
            return self.total_cost / Decimal(self.number_of_patients)
        except (ZeroDivisionError, InvalidOperation, TypeError):
            return 0

    def clean(self):
        if self.number_of_patients is not None and self.number_of_patients < 0:
            raise ValidationError("Number of patients cannot be negative.")
        if self.total_cost is not None and self.total_cost < 0:
            raise ValidationError("Total cost cannot be negative.")

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
    value = models.CharField(max_length=100)  # ✅ You added this
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
    

FREQUENCY_CHOICES = [
    ('hourly', 'Hourly'),
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
]

class AutomationSettings(models.Model):
    enabled = models.BooleanField(default=True)
    email_from = models.EmailField(blank=True, null=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')

    class Meta:
        verbose_name = "Automation Settings"
        verbose_name_plural = "Automation Settings"

    def __str__(self):
        return f"AutomationSettings (enabled={self.enabled})"


class OverduePaymentRule(models.Model):
    name = models.CharField(max_length=200)
    days_overdue = models.IntegerField(default=30)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    flag_reason = models.CharField(max_length=255, default="Overdue payment")
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LowInventoryRule(models.Model):
    name = models.CharField(max_length=200)
    threshold = models.IntegerField(default=10)
    enabled = models.BooleanField(default=True)
    email_recipients = models.TextField(blank=True, null=True)
    sms_recipients = models.TextField(blank=True, null=True)

    def get_email_list(self):
        return [e.strip() for e in (self.email_recipients or "").split(',') if e.strip()]

    def get_sms_list(self):
        return [p.strip() for p in (self.sms_recipients or "").split(',') if p.strip()]

    def __str__(self):
        return self.name


class ShiftSchedulingRule(models.Model):
    name = models.CharField(max_length=200)
    create_future_days = models.IntegerField(default=7)
    enabled = models.BooleanField(default=True)
    rotation_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AutomationLog(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    run_type = models.CharField(max_length=100)  # e.g., 'overdue', 'inventory', 'shifts'
    details = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.timestamp} - {self.run_type} - {'OK' if self.success else 'ERR'}"
    
# This allows admins to add/edit payment modes in the Django admin.
class PaymentModeReport(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Cash, POS, Mobile, Insurance
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Show in dashboard

    def __str__(self):
        return self.name 
