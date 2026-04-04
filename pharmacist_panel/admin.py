from django.contrib import admin
from .models import Medicine, Prescription
from .models import DispensationRecord

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'stock', 'expiry_date']
    list_filter = ['expiry_date']
    search_fields = ['name']

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'medicine', 'status', 'date']
    list_filter = ['status', 'date']
    search_fields = ['patient_name', 'medicine__name']

@admin.register(DispensationRecord)
class DispensationRecordAdmin(admin.ModelAdmin):
    list_display = ('date', 'patient_name', 'medicine', 'quantity', 'dispensed_by')
    list_filter = ('date', 'medicine', 'dispensed_by')
    search_fields = ('patient_name',)