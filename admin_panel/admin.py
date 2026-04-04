from django.contrib import admin
<<<<<<< HEAD
from .models import RevenueAging, CostPerPatient, InsuranceClaim, CashFlowForecast,KPITracking,ClinicalMetric,ClinicalComplication
=======
from .models import( RevenueAging, CostPerPatient, InsuranceClaim, CashFlowForecast,
KPITracking,ClinicalMetric,ClinicalComplication,AutomationSettings, OverduePaymentRule, LowInventoryRule,
ShiftSchedulingRule, AutomationLog
)
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf


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


<<<<<<< HEAD
=======
@admin.register(AutomationSettings)
class AutomationSettingsAdmin(admin.ModelAdmin):
    list_display = ('enabled', 'email_from', 'frequency')

@admin.register(OverduePaymentRule)
class OverduePaymentRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'days_overdue', 'min_amount', 'enabled')
    list_editable = ('days_overdue', 'min_amount', 'enabled')

@admin.register(LowInventoryRule)
class LowInventoryRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'threshold', 'enabled')

@admin.register(ShiftSchedulingRule)
class ShiftSchedulingRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_future_days', 'enabled', 'rotation_enabled')

@admin.register(AutomationLog)
class AutomationLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'run_type', 'success')
    readonly_fields = ('timestamp', 'run_type', 'details', 'success')

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
# Register your models here.
