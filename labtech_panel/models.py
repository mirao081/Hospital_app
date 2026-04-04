from django.db import models
from core.models import Patient, Doctor

class LabTestRequest(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    test_type = models.CharField(max_length=255)
    requested_at = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    result = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='lab_results/', blank=True, null=True)

    def __str__(self):
        return f"{self.test_type} for {self.patient}"

# Create your models here.
