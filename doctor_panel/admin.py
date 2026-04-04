from django.contrib import admin
<<<<<<< HEAD
from .models import MedicalRecord, Notification
=======
from .models import MedicalRecord, Notification,StaffMessage, ReferralRequest, PatientPortalRequest
from .models import AnalyticsConfig
from .forms import MedicalRecordForm
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'message', 'timestamp', 'read')
    list_filter = ('doctor', 'read', 'timestamp')
    search_fields = ('doctor__user__username', 'message')
    
<<<<<<< HEAD
admin.site.register(MedicalRecord)
=======
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    form = MedicalRecordForm
    fieldsets = (
        ('Patient & Doctor', {'fields': ('patient', 'doctor', 'appointment')}),
        ('Patient Info', {'fields': ('patient_age', 'patient_gender', 'patient_contact', 'patient_insurance')}),
        ('Clinical Data', {'fields': ('diagnosis', 'medications', 'prescription', 'lab_results', 'notes', 'imaging')}),
        ('Recent Interactions & Alerts', {'fields': ('last_visit', 'last_prescription', 'last_lab_results', 'critical_alerts',
                                                     'pending_tests', 'medication_management')}),
        ('Timestamps', {'fields': ('date_created',)}),
    )
    readonly_fields = ('date_created',)


@admin.register(StaffMessage)
class StaffMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at")
    search_fields = ("title", "message")
    list_filter = ("created_at",)


@admin.register(ReferralRequest)
class ReferralRequestAdmin(admin.ModelAdmin):
    list_display = ("patient_full_name", "from_staff_name", "to_staff_name", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("patient__user__first_name", "patient__user__last_name", "reason")

    def patient_full_name(self, obj):
        return obj.patient.user.get_full_name() if obj.patient else "Unknown"
    patient_full_name.short_description = "Patient"

    def from_staff_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.get_full_name()} ({obj.created_by_role})"
        return "Unknown"
    from_staff_name.short_description = "From Staff"


    def to_staff_name(self, obj):
        try:
            if obj.to_doctor and obj.to_doctor.user:
                return obj.to_doctor.user.get_full_name()
            elif obj.to_nurse:
                return obj.to_nurse.get_full_name()
            elif obj.to_pharmacist:
                return obj.to_pharmacist.get_full_name()
            elif obj.to_lab_tech:
                return obj.to_lab_tech.get_full_name()
        except Exception:
            return "Unknown"
        return "Unassigned"



@admin.register(PatientPortalRequest)
class PatientPortalRequestAdmin(admin.ModelAdmin):
    list_display = ("patient_name", "request_type", "doctor", "status", "created_at")
    list_filter = ("request_type", "status", "created_at")
    search_fields = ("patient_name", "message")

@admin.register(AnalyticsConfig)
class AnalyticsConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "default_date_range", "show_patient_counts", "show_case_mix", "show_outcomes", "revenue_enabled")
    list_editable = ("default_date_range", "show_patient_counts", "show_case_mix", "show_outcomes", "revenue_enabled")
    search_fields = ("name",)
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

# Register your models here.
