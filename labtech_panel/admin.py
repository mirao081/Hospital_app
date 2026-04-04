from django.contrib import admin
from .models import LabTestRequest

@admin.register(LabTestRequest)
class LabTestRequestAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test_type', 'status', 'requested_at')
    list_filter = ('status', 'test_type')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'test_type')

# Register your models here.
