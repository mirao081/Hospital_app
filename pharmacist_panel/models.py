from django.db import models
from django.utils import timezone
from core.models import Doctor
from django.conf import settings


class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ('Antibiotic', 'Antibiotic'),
        ('Painkiller', 'Painkiller'),
        ('Antiseptic', 'Antiseptic'),
        ('Supplement', 'Supplement'),
        # Add more categories as needed
    ]
    name = models.CharField(max_length=255)
    stock = models.PositiveIntegerField()
    batch_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True) 
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    def is_expiring_soon(self):
        return self.expiry_date <= timezone.now().date() + timezone.timedelta(days=30)

    def is_out_of_stock(self):
        return self.stock == 0

    def __str__(self):
        return f"{self.name} ({self.batch_number})"

class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('fulfilled', 'Fulfilled'),
    ]
    patient_name = models.CharField(max_length=255)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    doctor_name = models.CharField(max_length=255, blank=True)


    def __str__(self):
        return f"{self.patient_name} - {self.medicine.name}"
    
class DispensationRecord(models.Model):
    date = models.DateTimeField(default=timezone.now)  # Default timestamp
    patient_name = models.CharField(max_length=255)    # Patient's name
    medicine = models.ForeignKey('Medicine', on_delete=models.CASCADE)  # Link to medicine
    quantity = models.PositiveIntegerField()            # Dispensed quantity
    dispensed_by = models.ForeignKey(                   # Link to user
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"{self.patient_name} - {self.medicine.name} on {self.date.strftime('%Y-%m-%d')}"


class ReturnedMedicine(models.Model):
    date = models.DateTimeField(default=timezone.now)
    patient_or_ward = models.CharField(max_length=255)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    note = models.TextField(blank=True, null=True)

class WastageEntry(models.Model):
    date = models.DateTimeField(default=timezone.now)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    note = models.TextField(blank=True, null=True)


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField()

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    medicine_batch = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('received', 'Received')])
    order_date = models.DateField(auto_now_add=True)

class SupplierInvoice(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    invoice_file = models.FileField(upload_to='invoices/')
    approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)




# Create your models here.
