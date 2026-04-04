from django.db import models
from django.conf import settings
<<<<<<< HEAD
# from core.models import Patient
from django.apps import apps

User = settings.AUTH_USER_MODEL

=======
from django.apps import apps
import uuid
import random
import string
from django.utils.html import format_html
from django.utils import timezone
from datetime import datetime


User = settings.AUTH_USER_MODEL


>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('pos', 'POS (Card)'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile', 'Mobile Payment'),
        ('insurance', 'Insurance'),
    ]
<<<<<<< HEAD
    def get_patient_model():
        return apps.get_model('core', 'Patient')

    patient = models.ForeignKey(
        'core.Patient',  # ✅ use app_name.ModelName as string
        on_delete=models.CASCADE
    )

    
    patient_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_received = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient_name} - {self.amount} via {self.payment_method}"
=======

    SERVICE_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('surgery', 'Surgery'),
        ('lab', 'Laboratory'),
        ('radiology', 'Radiology'),
        ('pharmacy', 'Pharmacy'),
        ('admission', 'Admission'),
        ('appointment', 'Appointment'),
        ('other', 'Other'),
    ]

    patient = models.ForeignKey(
        'core.Patient',
        on_delete=models.CASCADE,
        related_name='payments'  # <-- Added related_name here
    )
    patient_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, default='other')
    reference_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_received = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    appointment = models.ForeignKey(
        'core.Appointment',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def generate_reference_number(self, style=1):
        """Generate professional reference numbers with multiple formats."""
        if style == 1:
            # Format: PAY-YYYYMMDD-XXXX
            return f"PAY-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        elif style == 2:
            # Format: INV-YYYY-000001 (incremental ID)
            last_id = Payment.objects.count() + 1
            return f"INV-{datetime.now().year}-{last_id:06d}"

        elif style == 3:
            # Format: REF-8HEX
            return f"REF-{uuid.uuid4().hex[:8].upper()}"

        elif style == 4:
            # Format: TRX-YYYYMMDD-HHMMSS
            return f"TRX-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        elif style == 5:
            # Format: HOSPYY-XXXXXX
            return f"HOSP{datetime.now().strftime('%y')}-" + ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Try to generate a unique reference number
            ref = self.generate_reference_number(style=1)  # change style number here if you want
            while Payment.objects.filter(reference_number=ref).exists():
                ref = self.generate_reference_number(style=1)
            self.reference_number = ref
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_name} - {self.amount} via {self.payment_method} - {self.reference_number}"
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf


class Invoice(models.Model):
    patient = models.ForeignKey(
<<<<<<< HEAD
        'core.Patient',  # lazy reference
        on_delete=models.CASCADE
=======
        'core.Patient',
        on_delete=models.CASCADE,
        related_name='invoices'
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    )

    SERVICE_CHOICES = [
        ('consultation', 'Consultation'),
        ('lab', 'Lab Test'),
        ('surgery', 'Surgery'),
        ('pharmacy', 'Pharmacy'),
<<<<<<< HEAD
=======
        ('appointment', 'Appointment'),
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        ('others', 'Other Services'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

<<<<<<< HEAD
=======
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('unpaid', 'Unpaid'),
    ]

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    service_date = models.DateField()
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    invoice_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_generated = models.DateTimeField(auto_now_add=True)
<<<<<<< HEAD
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Invoice for {self.patient} - {self.invoice_number} ({self.status})"
=======

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # New payment tracking fields
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')

    # Flag overdue invoices automatically
    is_flagged = models.BooleanField(default=False, help_text="Automatically flagged as overdue by the system")

    def save(self, *args, **kwargs):
        # Update payment status automatically based on amount_paid and total_due
        if self.amount_paid >= self.total_due:
            self.payment_status = 'paid'
        elif 0 < self.amount_paid < self.total_due:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'unpaid'

        # Automatically flag overdue invoices (past due_date and not paid)
        self.is_flagged = self.due_date < timezone.now().date() and self.payment_status != 'paid'

        super().save(*args, **kwargs)

    def payment_status_display(self):
        # Color coding for payment status
        colors = {
            'paid': 'green',
            'partial': 'orange',
            'unpaid': 'red',
        }
        color = colors.get(self.payment_status, 'black')
        overdue_icon = ' ⚠️' if self.is_flagged else ''

        return format_html(
            '<span style="color: {};">{} {}</span>',
            color,
            self.get_payment_status_display(),
            overdue_icon
        )

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.patient} - Status: {self.status}, Payment: {self.payment_status}"
    
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.amount}"


class Refund(models.Model):
<<<<<<< HEAD
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
=======
    payment = models.ForeignKey(
        'Payment', on_delete=models.CASCADE, related_name='refunds'
    )
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    issue_date = models.DateTimeField(auto_now_add=True)

    # Approval fields
<<<<<<< HEAD
    is_approved = models.BooleanField(null=True, default=None)  # None = pending
=======
    is_approved = models.BooleanField(null=True, blank=True)  # None = pending
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds_approved_cashier'
    )
    admin_note = models.TextField(blank=True, null=True)

<<<<<<< HEAD
    def approval_status(self):
=======
    @property
    def approval_status(self):
        """Return string status: Approved / Rejected / Pending"""
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        if self.is_approved is None:
            return "Pending"
        return "Approved" if self.is_approved else "Rejected"

    def __str__(self):
        return f"Refund: {self.payment.patient_name} - {self.refund_amount}"

<<<<<<< HEAD
=======
class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('refund_approval', 'Pending Refund/Adjustment Approval'),
        ('large_balance', 'Patient with Large Outstanding Balance'),
        ('invoice_discrepancy', 'Invoice Discrepancy or Error'),
    ]

    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    description = models.TextField(help_text="Details about the alert")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    is_critical = models.BooleanField(default=False)  # NEW FIELD

    def __str__(self):
        return f"{self.get_alert_type_display()} - {'Resolved' if self.is_resolved else 'Pending'}"

class DashboardSection(models.Model):
    """
    Simple CMS-like block for editable dashboard content.
    Use key='insurance_payer_info' for this specific section.
    """
    key = models.SlugField(unique=True)  # e.g. "insurance_payer_info"
    title = models.CharField(max_length=255, default="Insurance & Third-Party Payer Information")
    body = models.TextField(
        blank=True,
        default="Show insurance coverage details if applicable\n\n"
                "Indicate which payments are made by insurance and which are patient out-of-pocket\n\n"
                "Why: Many hospitals work with insurance; cashiers need to track these separately."
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard Section"
        verbose_name_plural = "Dashboard Sections"

    def __str__(self):
        return self.title
    
class AccountNote(models.Model):
    patient = models.ForeignKey('core.Patient', on_delete=models.CASCADE)
    
    invoice = models.ForeignKey(
        'cashier.Invoice',  # or 'billing.Invoice' if Invoice is in another app
        related_name='account_notes',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    note = models.TextField()
    is_pinned = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_account_notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-is_pinned', '-created_at')
        indexes = [
            models.Index(fields=['-is_pinned', '-created_at']),
        ]

    def __str__(self):
        inv = f" • Inv #{self.invoice.invoice_number}" if self.invoice else ""
        return f"Note for {self.patient} {inv}"
    
    
class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True, help_text="Currency code (e.g. USD, EUR, NGN)")
    name = models.CharField(max_length=50, help_text="Full name of the currency")
    symbol = models.CharField(max_length=5, help_text="Symbol (e.g. $, €, ₦)")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, help_text="Rate against base currency (e.g. 1 USD = X Local Currency)")
    is_base = models.BooleanField(default=False, help_text="Mark only ONE as base currency")

    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.code} ({self.symbol})"
    

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("VIEW", "View"),
        ("PIN_NOTE", "Pinned Note"),
        ("UNPIN_NOTE", "Unpinned Note"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model = models.CharField(max_length=100)  # e.g. "Invoice", "PatientNote"
    object_id = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} {self.model} ({self.timestamp})"
    
class UserSessionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="session_logs")
    login_time = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)  # auto-updates whenever saved
    logout_time = models.DateTimeField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Session for {self.user.username} at {self.login_time.strftime('%Y-%m-%d %H:%M')}"
    
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

# Create your models here.
