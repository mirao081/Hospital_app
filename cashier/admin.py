from django.contrib import admin
from .models import Payment, Invoice, InvoiceItem, Refund
<<<<<<< HEAD


admin.site.register(Payment)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
=======
from .models import Alert,DashboardSection,Currency,AccountNote
from core.models import PatientNote


>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('payment', 'refund_amount', 'issued_by', 'issue_date')
<<<<<<< HEAD
    search_fields = ('payment__patient_name', 'issued_by__username')

# Register your models here.
=======
    search_fields = ('payment__patient__name', 'issued_by__username')  # corrected double underscore


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient', 'amount_due', 'amount_paid', 'status', 'due_date', 'is_overdue', 'payment_status_display')
    list_filter = ('status',)
    search_fields = ('invoice_number', 'patient__name')
    readonly_fields = ('payment_status_display',)

    # Define amount_due method to expose the @property to admin
    def amount_due(self, obj):
        return obj.amount_due
    amount_due.admin_order_field = 'total_due'
    amount_due.short_description = 'Amount Due'

    # Define is_overdue method properly
    def is_overdue(self, obj):
        # assuming your model has `is_flagged` to mark overdue
        return obj.is_flagged
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue?'

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'description', 'created_at', 'is_resolved')
    list_filter = ('alert_type', 'is_resolved')
    search_fields = ('description',)
    readonly_fields = ('created_at',)

@admin.register(DashboardSection)
class DashboardSectionAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("key", "title", "body")
    fieldsets = (
        (None, {"fields": ("key", "is_active")}),
        ("Content", {"fields": ("title", "body")}),
    )

@admin.register(AccountNote)
class AccountNoteAdmin(admin.ModelAdmin):
    list_display = ('patient', 'invoice', 'short_note', 'is_pinned', 'created_by', 'created_at')
    list_filter = ('is_pinned', 'created_at')
    search_fields = ('note', 'patient__user__first_name', 'patient__user__last_name', 'patient__user__username', 'invoice__invoice_number')
    autocomplete_fields = ('patient', 'invoice')

    def short_note(self, obj):
        return (obj.note[:80] + '…') if len(obj.note) > 80 else obj.note
    short_note.short_description = 'Note'

@admin.register(PatientNote)
class PatientNoteAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created_by', 'created_at', 'updated_at')
    search_fields = ('patient__user__username', 'patient__user__first_name', 'note')
    list_filter = ('created_at',)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol", "exchange_rate", "is_base")
    list_editable = ("exchange_rate",)
    list_filter = ("is_base",)

admin.site.register(Payment)
admin.site.register(InvoiceItem)
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
