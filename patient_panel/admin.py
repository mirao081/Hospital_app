from django.contrib import admin
from .models import Diagnosis, Treatment, Medication, LabResult, Visit,Bill



@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('patient', 'amount', 'description', 'date_issued', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('patient__username', 'description')

admin.site.register(Diagnosis)
admin.site.register(Treatment)
admin.site.register(Medication)
admin.site.register(LabResult)
admin.site.register(Visit)
