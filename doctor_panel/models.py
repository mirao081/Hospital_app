from django.db import models
from django.conf import settings
from core.models import Doctor, Patient, Appointment
from core.utils import get_staff_role
from django.contrib.auth import get_user_model

User = get_user_model()

class MedicalRecord(models.Model):
    """Stores clinical & medical data for patients."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_records")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name="medical_records")
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True)

    # Patient snapshot (copied when record is created)
    patient_age = models.PositiveIntegerField(null=True, blank=True)
    patient_gender = models.CharField(max_length=20, blank=True)
    patient_contact = models.CharField(max_length=100, blank=True)
    patient_insurance = models.CharField(max_length=200, blank=True)

    # Clinical fields
    diagnosis = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    lab_results = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    imaging = models.ImageField(upload_to='medical_images/', blank=True, null=True)

    # Structured fields
    last_visit = models.DateTimeField(blank=True, null=True)
    last_prescription = models.TextField(blank=True)
    last_lab_results = models.TextField(blank=True)
    critical_alerts = models.TextField(blank=True)
    pending_tests = models.TextField(blank=True)
    medication_management = models.TextField(blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-fill patient info if not already set."""
        if self.patient:
            if self.patient_age is None and hasattr(self.patient, "age"):
                self.patient_age = self.patient.age
            if not self.patient_gender and hasattr(self.patient, "gender"):
                self.patient_gender = self.patient.gender
            if not self.patient_contact and hasattr(self.patient, "contact"):
                self.patient_contact = self.patient.contact
            if not self.patient_insurance and hasattr(self.patient, "insurance_info"):
                self.patient_insurance = self.patient.insurance_info
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.diagnosis[:30]}"


class Notification(models.Model):
    """System notifications for doctors."""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.doctor.user.get_full_name()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Interaction(models.Model):
    """Doctor-patient interaction log."""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="interactions")
    # make patient optional so old rows can stay NULL; avoids interactive prompt
    patient = models.ForeignKey(
    Patient,
    on_delete=models.SET_NULL,
    related_name="interactions",   # or "diagnostic_tests" depending on model
    null=True,
    blank=True,
)

    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Interaction with {self.patient.user.get_full_name() if self.patient else 'Unknown'} on {self.date.strftime('%Y-%m-%d')}"


class DiagnosticTest(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="diagnostic_tests")
    # make patient optional for migration safety
    patient = models.ForeignKey(
    Patient,
    on_delete=models.SET_NULL,
    related_name="diagnostic_tests",   # or "diagnostic_tests" depending on model
    null=True,
    blank=True,
)

    patient_name = models.CharField(max_length=100, blank=True)
    test_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.test_name} for {self.patient_name} ({self.status})"


class StaffMessage(models.Model):
    """Internal staff messages/announcements."""
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_messages_created"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class ReferralRequest(models.Model):
    # Sender (the person who created the referral)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals_created"
    )
    created_by_role = models.CharField(max_length=50, blank=True, null=True)

    # Recipient (generic user)
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals_received"
    )

    # Doctor-specific recipient
    to_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="doctor_referrals",
        null=True,
        blank=True
    )

    # Patient being referred
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        related_name="referrals",
        null=True,
        blank=True
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined')
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.created_by and not self.created_by_role:
            self.created_by_role = get_staff_role(self.created_by)
        super().save(*args, **kwargs)

    # ---------- Computed "from_*" properties ----------
    @property
    def from_doctor(self):
        """Return Doctor object if the referral was created by a doctor."""
        if self.created_by_role and self.created_by_role.lower() == "doctor":
            return Doctor.objects.filter(user=self.created_by).first()
        return None

    def __str__(self):
        patient_name = self.patient.user.get_full_name() if self.patient else "Unknown"
        from_staff = (
            f"{self.created_by.get_full_name()} ({self.created_by_role})"
            if self.created_by else "Unknown"
        )
        to_staff = (
            self.to_doctor.user.get_full_name() if self.to_doctor else
            self.to_user.get_full_name() if self.to_user else
            "Unassigned"
        )
        return f"Referral: {patient_name} from {from_staff} → {to_staff}"

class PatientPortalRequest(models.Model):
    """Requests/questions from patients via portal."""
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="portal_requests",
        null=True, blank=True
    )
    patient_name = models.CharField(max_length=255)
    patient_contact = models.CharField(max_length=100, blank=True, null=True)
    request_type = models.CharField(
        max_length=50,
        choices=[('question', 'Question'), ('followup', 'Follow-up'), ('teleconsultation', 'Teleconsultation')],
    )
    message = models.TextField()
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="patient_requests"
    )
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_name} - {self.request_type}"


class AnalyticsConfig(models.Model):
    """A simple config to control which analytics widgets show and some thresholds.
    Editable from Django Admin.


    You can expand this with per-doctor defaults, custom colors, or saved filters.
    """
    name = models.CharField(max_length=120, default="Default Analytics Config")


    show_patient_counts = models.BooleanField(default=True)
    show_case_mix = models.BooleanField(default=True)
    show_outcomes = models.BooleanField(default=True)
    show_revenue = models.BooleanField(default=False)


    # default date range choices (you can override in the URL / front-end)
    DATE_RANGE_CHOICES = [
    ("day", "Today"),
    ("week", "This week"),
    ("month", "This month"),
    ("quarter", "This quarter"),
    ]
    default_date_range = models.CharField(max_length=10, choices=DATE_RANGE_CHOICES, default="day")


    # thresholds for highlighting
    followup_rate_threshold = models.FloatField(default=0.6, help_text="If follow-up rate < this, show alert")


    revenue_enabled = models.BooleanField(default=False, help_text="Enable revenue metrics (if you store billing data)")


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Analytics configuration"
        verbose_name_plural = "Analytics configurations"


# class DoctorTask(models.Model):
#     doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     is_completed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     due_date = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return self.title

# class DoctorReminder(models.Model):
#     doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
#     message = models.CharField(max_length=255)
#     follow_up_days = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.message} ({self.follow_up_days} days)"

# class OnCallSchedule(models.Model):
#     doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='oncall_shifts')
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()
#     notes = models.TextField(blank=True)

#     def __str__(self):
#         return f"{self.doctor.username}: {self.start_time} - {self.end_time}"

# class KnowledgeBaseEntry(models.Model):
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.title