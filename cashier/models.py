from django.db import models
from django.conf import settings
# from core.models import Patient
from django.apps import apps

User = settings.AUTH_USER_MODEL

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('pos', 'POS (Card)'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile', 'Mobile Payment'),
        ('insurance', 'Insurance'),
    ]
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


class Invoice(models.Model):
    patient = models.ForeignKey(
        'core.Patient',  # lazy reference
        on_delete=models.CASCADE
    )

    SERVICE_CHOICES = [
        ('consultation', 'Consultation'),
        ('lab', 'Lab Test'),
        ('surgery', 'Surgery'),
        ('pharmacy', 'Pharmacy'),
        ('others', 'Other Services'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

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
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Invoice for {self.patient} - {self.invoice_number} ({self.status})"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.amount}"


class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    issue_date = models.DateTimeField(auto_now_add=True)

    # Approval fields
    is_approved = models.BooleanField(null=True, default=None)  # None = pending
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds_approved_cashier'
    )
    admin_note = models.TextField(blank=True, null=True)

    def approval_status(self):
        if self.is_approved is None:
            return "Pending"
        return "Approved" if self.is_approved else "Rejected"

    def __str__(self):
        return f"Refund: {self.payment.patient_name} - {self.refund_amount}"


# Create your models here.
