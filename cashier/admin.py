from django.contrib import admin
from .models import Payment, Invoice, InvoiceItem, Refund


admin.site.register(Payment)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('payment', 'refund_amount', 'issued_by', 'issue_date')
    search_fields = ('payment__patient_name', 'issued_by__username')

# Register your models here.
