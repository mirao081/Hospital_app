from django.db import models
from core.models import Doctor, Patient

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='records')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    diagnosis = models.TextField()
    lab_results = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    imaging = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.date_created.strftime('%Y-%m-%d')}"


class Notification(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.doctor} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


# Create your models here.
