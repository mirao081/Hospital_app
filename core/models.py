from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from cashier.models import Payment






class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('pharmacist', 'Pharmacist'),
        ('labtech', 'Lab Technician'),
        ('patient', 'Patient'),
        ('cashier', 'Cashier'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

class HeaderSettings(models.Model):
    hospital_name = models.CharField(max_length=100, default='My Hospital')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    

    menu_1 = models.CharField(max_length=50, default='Home')
    menu_2 = models.CharField(max_length=50, default='Services')
    menu_3 = models.CharField(max_length=50, default='Doctors')
    menu_4 = models.CharField(max_length=50, default='Departments')
    menu_5 = models.CharField(max_length=50, default='Appointments')
    menu_6 = models.CharField(max_length=50, default='About')
    menu_7 = models.CharField(max_length=50, default='Contact')

     # New topbar fields
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    working_hours = models.CharField(max_length=100, default="Monday - Friday, 8AM to 10PM")


    def __str__(self):
        return "Header Settings"
    
class Department(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='departments/', blank=True, null=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    
    is_featured = models.BooleanField(default=False)
    appointments_completed = models.PositiveIntegerField(default=0)
    start_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)  # ✅ Add this
    specialty = models.CharField(max_length=100, blank=True, null=True)    # ✅ Add this

    def __str__(self):
        if self.user:
            full_name = self.user.get_full_name()
            return full_name.strip() or self.user.username
        return "Unnamed Doctor"


# models.py
class Appointment(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, related_name='appointments')
    datetime = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)  # ✅ Add this
    location = models.CharField(max_length=255, blank=True, null=True)  # ✅ Add this
    send_reminder = models.BooleanField(default=False)  # ✅ Add this
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(max_length=20, default="Pending", choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ])

    status = models.CharField(max_length=20, default="Scheduled", choices=[
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Missed', 'Missed'),
        ('Cancelled', 'Cancelled'),
    ])

    def __str__(self):
        patient_name = self.full_name or "Unknown"
        if self.doctor and self.doctor.user:
            doctor_name = self.doctor.user.get_full_name() or self.doctor.user.username
        else:
            doctor_name = "Unknown Doctor"
        return f"{patient_name} with {doctor_name} on {self.datetime.strftime('%Y-%m-%d %H:%M')}"


class Specialty(models.Model):
    name = models.CharField(max_length=100)
    doctor_count = models.PositiveIntegerField()
    image = models.ImageField(upload_to='specialties/')

    def __str__(self):
        return self.name
    
class AboutSection(models.Model):
    heading = models.CharField(max_length=200)
    paragraph = models.TextField()
    bullet_points = models.TextField(help_text="Enter 6 items separated by semicolon ';'")
    image1 = models.ImageField(upload_to='about/')
    image2 = models.ImageField(upload_to='about/')
    moving_text = models.CharField(max_length=200)

    def get_bullet_list(self):
        return [item.strip() for item in self.bullet_points.split(';') if item.strip()]

    def __str__(self):
        return self.heading
    
class FeaturedDoctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='doctors/')
    appointments_completed = models.PositiveIntegerField(default=0)
    start_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class HighlightItem(models.Model):
    image = models.ImageField(upload_to='highlight/')
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)

    def __str__(self):
        return self.title
    
class InfoCard(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(upload_to='info_cards/')
    paragraph = models.TextField()

    def __str__(self):
        return self.title
    
class UserReview(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='review_photos/')
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)  # max 5 stars

    def __str__(self):
        return f"{self.name} ({self.address})"
    
class Article(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='articles/')
    category = models.CharField(max_length=50)  # e.g. "Health Tips"
    date_published = models.DateField(auto_now_add=True)
    excerpt = models.TextField()

    def __str__(self):
        return self.title
    
class DoctorCTA(models.Model):
    heading = models.CharField(max_length=255, help_text="Use five words. The third will be styled violet.")
    description = models.TextField()
    button_text = models.CharField(max_length=50, default="View all doctors")
    image = models.ImageField(upload_to='cta_images/')

    def __str__(self):
        return "Doctor Call To Action Section"
    
class FooterSettings(models.Model):
    copyright_text = models.CharField(max_length=255, default="© 2025 New-Life Clinic")
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Footer Settings"
    
class DoctorsPageSettings(models.Model):
    title = models.CharField(max_length=100, default="Doctors")
    breadcrumb_home_text = models.CharField(max_length=50, default="Home")
    background_color = models.CharField(max_length=30, default="aliceblue")
    height = models.CharField(max_length=10, default="45vh")

    def __str__(self):
        return "Doctors Page Settings"
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    
class Blog(models.Model):
    CATEGORY_CHOICES = [
        ('Patient Guide', 'Patient Guide'),
        ('Wellness', 'Wellness'),
        ('Immunization', 'Immunization'),
        ('Preventive Care', 'Preventive Care'),
        ('Recovery', 'Recovery'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Health')  # <-- NEW
    date_published = models.DateField(auto_now_add=True)  # <-- NEW
    created_at = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=100, blank=True, help_text="Optional label shown on image e.g. 'Updates', 'Health Tips'")

    def __str__(self):
        return self.title

    
class FeaturedBlog(models.Model):
    CATEGORY_COLORS = [
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_COLORS, default='blue')
    image = models.ImageField(upload_to='blogs/')
    date_published = models.DateField()
    excerpt = models.TextField()
    
    def __str__(self):
        return self.title
    

# core/models.py



class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='testimonials/')
    quote = models.TextField()
    rating = models.IntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)], default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.location})"
    
class ContactInfo(models.Model):
    country = models.CharField(max_length=100)
    address = models.TextField()
    email_info = models.TextField()
    email = models.EmailField()
    phone_info = models.TextField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.country


class Enquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)  # 🔥 Add this field
    created_at = models.DateTimeField(auto_now_add=True)  # Optional but useful

    def __str__(self):
        return f"Enquiry from {self.name}"
# core/models.py

class Room(models.Model):
    number = models.CharField(max_length=10, unique=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.number}"

class Bed(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=10)
    is_occupied = models.BooleanField(default=False)
    patient = models.OneToOneField('Patient', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Bed {self.bed_number} in {self.room.number}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    REFERRAL_CHOICES = [
        ('walk-in', 'Walk-in'),
        ('referral', 'Referral'),
        ('ads', 'Advertisement'),
        ('online', 'Online Search'),
        ('other', 'Other'),
    ]
    referral_source = models.CharField(
    max_length=20,
    choices=REFERRAL_CHOICES,
    blank=False,
    null=False
)

    
    @property
    def full_name(self):
        if self.user.first_name or self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return self.user.username

    def __str__(self):
        return self.full_name

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('REGISTER', 'User Registered'),
        ('APPOINTMENT', 'Appointment Booked'),
        ('TEST_RESULT', 'Lab Result Uploaded'),
        ('PRESCRIPTION', 'Prescription Issued'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_action_display()} by {self.user} at {self.timestamp}"
    
# models.py (in pharmacy or lab app)

class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('Pharmacy', 'Pharmacy'),
        ('Lab Equipment', 'Lab Equipment'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField()
    threshold = models.PositiveIntegerField(default=10)  # minimum acceptable quantity
    updated_at = models.DateTimeField(auto_now=True)

    def is_low_stock(self):
        return self.quantity < self.threshold

    def __str__(self):
        return f"{self.name} ({self.category})"
    
class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # e.g., Doctor, Nurse, Lab Tech

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
class Shift(models.Model):
    SHIFT_CHOICES = [
        ("Morning", "Morning"),
        ("Afternoon", "Afternoon"),
        ("Night", "Night"),
    ]

    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    date = models.DateField()
    shift_type = models.CharField(max_length=20, choices=SHIFT_CHOICES)

    class Meta:
        unique_together = ('staff', 'date', 'shift_type')

    def __str__(self):
        return f"{self.staff} - {self.shift_type} shift on {self.date}"


class Attendance(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    date = models.DateField()
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"),
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Late", "Late"),
    ], default="Pending")

    class Meta:
        unique_together = ('staff', 'date', 'shift')

class StaffAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"
    
class RefundRequest(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_refunds')
    approved_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='refunds_approved_core'
)

    approval_status = models.CharField(max_length=10, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    admin_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund #{self.id} for Payment {self.payment.id}"
    

# core/models.py

class Admission(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    admitted_at = models.DateTimeField()
    bed_assigned_at = models.DateTimeField(null=True, blank=True)
    discharged_at = models.DateTimeField(null=True, blank=True)
    outcome = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.full_name} admission"



class SurveyResponse(models.Model):
    SATISFACTION_CHOICES = [
        (1, 'Very Dissatisfied'),
        (2, 'Dissatisfied'),
        (3, 'Neutral'),
        (4, 'Satisfied'),
        (5, 'Very Satisfied'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='surveys')
    visit_date = models.DateField()
    satisfaction_score = models.IntegerField(choices=SATISFACTION_CHOICES)
    comments = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Survey by {self.patient} on {self.visit_date}"


class AppointmentReminder(models.Model):
    REMINDER_METHOD_CHOICES = [
        ('SMS', 'SMS'),
        ('Email', 'Email'),
        ('Phone', 'Phone Call'),
    ]

    REMINDER_STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='reminders'
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='reminders',
        null=True,  # Optional if some reminders are generic
        blank=True
    )

    appointment_date = models.DateTimeField()  # Ideally this should match appointment.date + time

    reminder_sent_at = models.DateTimeField(default=timezone.now)

    via = models.CharField(
        max_length=20,
        choices=REMINDER_METHOD_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=REMINDER_STATUS_CHOICES,
        default='sent'
    )

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        appointment_info = f" for appointment on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}" if self.appointment_date else ""
        return f"Reminder to {self.patient.full_name}{appointment_info} via {self.via}"

    class Meta:
        ordering = ['-reminder_sent_at']
        verbose_name = "Appointment Reminder"
        verbose_name_plural = "Appointment Reminders"


class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('praise', 'Praise'),
        ('other', 'Other'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Feedback or Complaint"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.feedback_type.title()} - {self.subject}"

# Create your models here.
