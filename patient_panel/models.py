from django.db import models
from django.conf import settings
from core.models import Patient, Appointment

class Diagnosis(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnoses')
    diagnosis = models.TextField()
    date_diagnosed = models.DateField()

class Treatment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatments')
    treatment = models.TextField()
    condition = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

class Medication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    prescribed_date = models.DateField()

class LabResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    test_name = models.CharField(max_length=255)
    result = models.TextField()
    date_taken = models.DateField()

class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    visit_date = models.DateField()
    reason = models.CharField(max_length=255)
    is_upcoming = models.BooleanField(default=False)

    # Add these new fields for timing analysis
    check_in_time = models.DateTimeField(null=True, blank=True)
    seen_by_doctor_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Visit on {self.visit_date} for {self.patient.full_name}"

class Bill(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bills')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date_issued = models.DateField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.description} - ₦{self.amount} ({'Paid' if self.is_paid else 'Unpaid'})"
