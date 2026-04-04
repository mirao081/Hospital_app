from django.db import models
from django.conf import settings
from core.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()



# Daily round notes model
class DailyRound(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Round for {self.patient.full_name} on {self.recorded_at.date()}"


# Medication/dressing reminders
class Reminder(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    scheduled_time = models.DateTimeField()

    def __str__(self):
        return f"Reminder for {self.patient.user.get_full_name()}: {self.message}"


# Vitals model
class Vitals(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    temperature = models.FloatField()
    blood_pressure = models.CharField(max_length=20)
    heart_rate = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} - {self.recorded_at.date()}"


# nurse_panel/models.py

class NurseTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    patient = models.ForeignKey('core.Patient', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
    

class MedicationOrder(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    prescribed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prescriptions', limit_choices_to={'role': 'doctor'})
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    instructions = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.medication_name} - {self.patient.get_full_name()}"


class MedicationLog(models.Model):
    order = models.ForeignKey(MedicationOrder, on_delete=models.CASCADE)
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'nurse'})
    administered_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('given', 'Given'),
        ('skipped', 'Skipped'),
        ('adjusted', 'Adjusted'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.order.medication_name} - {self.status} ({self.administered_at})"


class MedicationRequest(models.Model):
    nurse = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'nurse'})
    medication_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    reason = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medication_name} ({self.quantity}) - {self.nurse.get_full_name()}"
