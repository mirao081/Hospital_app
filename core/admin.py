from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    HeaderSettings, Department, Service, Doctor, Appointment,
    Specialty, AboutSection, HighlightItem, InfoCard, UserReview,
    Article, DoctorCTA, FooterSettings, DoctorsPageSettings,
    Blog, FeaturedBlog, Category, Testimonial,
    ContactInfo, Enquiry, Room, Bed, Message,
    User, Patient, FeaturedDoctor, Shift, StaffProfile, Admission,
    SurveyResponse, AppointmentReminder, Feedback
)

# ------------------- Inlines -------------------
class PatientInline(admin.StackedInline):
    model = Patient
    can_delete = False
    verbose_name_plural = 'Patient Info'

# ------------------- Custom User Admin -------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [PatientInline]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Role info'), {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

# ------------------- Patient Admin -------------------
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'age', 'gender', 'phone', 'referral_source_label']

    def referral_source_label(self, obj):
        return obj.get_referral_source_display()
    referral_source_label.short_description = "Referral Source"

# ------------------- Doctor Admin -------------------
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'department', 'is_featured', 'appointments_completed', 'start_price']
    list_filter = ['is_featured', 'department']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']

# ------------------- Article Admin -------------------
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_published')
    list_filter = ('category', 'date_published')

# ------------------- Doctors Page Settings -------------------
@admin.register(DoctorsPageSettings)
class DoctorsPageSettingsAdmin(admin.ModelAdmin):
    list_display = ['title', 'breadcrumb_home_text', 'background_color', 'height']

# ------------------- Blog Admin -------------------
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    prepopulated_fields = {"slug": ("title",)}

# ------------------- Testimonial Admin -------------------
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'rating', 'created_at']
    search_fields = ['name', 'location', 'quote']

# ------------------- Appointment Admin -------------------
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'doctor', 'get_date', 'get_time', 'payment_status', 'status')
    search_fields = ('full_name', 'email', 'doctor__user__first_name', 'doctor__user__last_name')
    list_filter = ('payment_status', 'status', 'datetime')
    ordering = ('-datetime',)

    fieldsets = (
        ('Patient Info', {'fields': ('full_name', 'email', 'phone')}),
        ('Appointment Details', {'fields': ('doctor', 'datetime', 'comment', 'status')}),
        ('Payment Info', {'fields': ('payment_amount', 'payment_status')}),
    )

    @admin.display(description='Date')
    def get_date(self, obj):
        return obj.datetime.date()

    @admin.display(description='Time')
    def get_time(self, obj):
        return obj.datetime.time()


# ------------------- Room and Bed Admin -------------------
class BedInline(admin.TabularInline):
    model = Bed
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number',)
    inlines = [BedInline]

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'room', 'is_occupied')
    list_filter = ('room', 'is_occupied')

# ------------------- Enquiry Admin -------------------
@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'country', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')

# ------------------- Featured Doctor Admin -------------------
@admin.register(FeaturedDoctor)
class FeaturedDoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'appointments_completed', 'start_price')
    search_fields = ('name', 'specialty')

# ------------------- Shift Admin -------------------
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'shift_type')
    list_filter = ('shift_type', 'date')
    search_fields = ('staff__user__first_name', 'staff__user__last_name')

# ------------------- Staff Profile Admin -------------------
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')

# ------------------- Admission Admin -------------------
@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'admitted_at', 'bed_assigned_at', 'discharged_at']
    list_filter = ['admitted_at', 'discharged_at']
    search_fields = ['patient__user__first_name', 'patient__user__last_name']

# ------------------- Survey Response Admin -------------------
@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('patient', 'satisfaction_score', 'submitted_at')
    search_fields = ('patient__user__first_name', 'patient__user__last_name')
    list_filter = ('submitted_at',)
    ordering = ('-submitted_at',)
    date_hierarchy = 'submitted_at'

# ------------------- Appointment Reminder Admin -------------------
@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ('patient', 'appointment_date', 'via', 'status')
    search_fields = ('patient__user__first_name', 'patient__user__last_name')
    list_filter = ('status', 'via', 'appointment_date')
    ordering = ('-appointment_date',)

# ------------------- Feedback Admin -------------------
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('patient', 'feedback_type', 'submitted_at', 'resolved')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'message')
    list_filter = ('feedback_type', 'resolved')
    ordering = ('-submitted_at',)

# ------------------- Register Remaining Models -------------------
admin.site.register(HeaderSettings)
admin.site.register(Department)
admin.site.register(Service)
admin.site.register(Specialty)
admin.site.register(AboutSection)
admin.site.register(HighlightItem)
admin.site.register(InfoCard)
admin.site.register(UserReview)
admin.site.register(DoctorCTA)
admin.site.register(FooterSettings)
admin.site.register(FeaturedBlog)
admin.site.register(Category)
admin.site.register(ContactInfo)
admin.site.register(Message)
