from django.contrib import admin
from .models import RevenueAging, CostPerPatient, InsuranceClaim, CashFlowForecast,KPITracking,ClinicalMetric,ClinicalComplication


@admin.register(RevenueAging)
class RevenueAgingAdmin(admin.ModelAdmin):
    list_display = ('bill_reference', 'patient', 'amount_due', 'due_date', 'days_overdue')
    readonly_fields = ('bill_reference',)  # Makes it visible but not editable



@admin.register(CostPerPatient)
class CostPerPatientAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_cost', 'number_of_patients', 'cost_per_visit')


@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_id', 'patient_name', 'amount_claimed', 'insurer', 'date_submitted', 'status')
    list_filter = ('status', 'insurer')


@admin.register(CashFlowForecast)
class CashFlowForecastAdmin(admin.ModelAdmin):
    list_display = ('forecast_month', 'expected_income', 'expected_expenses', 'net_cash_flow')


@admin.register(KPITracking)
class KPITrackingAdmin(admin.ModelAdmin):
    list_display = ('feature', 'importance')
    search_fields = ('feature',)

@admin.register(ClinicalMetric)
class ClinicalMetricAdmin(admin.ModelAdmin):
    list_display = ('metric_type', 'value', 'updated_at')
    list_filter = ('metric_type',)
    search_fields = ('metric_type', 'value')

@admin.register(ClinicalComplication)
class ClinicalComplicationAdmin(admin.ModelAdmin):
    list_display = ('complication_type', 'admission', 'reported_at')
    list_filter = ('reported_at', 'complication_type')
    search_fields = ('complication_type', 'notes')
    fields = ('admission', 'complication_type', 'notes', 'reported_at')  # ✅ Add this line


# Register your models here.
