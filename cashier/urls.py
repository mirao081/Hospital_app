# cashier/urls.py
from django.urls import path
from . import views
<<<<<<< HEAD


app_name = 'cashier'  # Enables namespaced URL resolution in templates

urlpatterns = [
    path('', views.cashier_dashboard),
    path('dashboard/', views.cashier_dashboard, name='cashier_dashboard'),
    path('record-payment/', views.record_payment, name='cashier_record_payment'),
    path('payments/', views.payment_list, name='cashier_payment_list'),
=======
from .views import get_patient_billing_info

app_name = 'cashier'

urlpatterns = [
    # Cashier dashboard
    path('', views.cashier_dashboard, name='cashier_dashboard'),

    # Payment management
    path('record-payment/', views.record_payment, name='cashier_record_payment'),
    path('payments/', views.payment_list, name='cashier_payment_list'),

    # Invoice management
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    path('generate-invoice/', views.generate_invoice, name='cashier_generate_invoice'),
    path('invoices/', views.invoice_list, name='cashier_invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/edit/', views.edit_invoice, name='edit_invoice'),
    path('invoices/<int:invoice_id>/delete/', views.delete_invoice, name='delete_invoice'),
    path('invoices/<int:invoice_id>/print/', views.print_invoice, name='print_invoice'),

    # Refund functionality
    path('refund/<int:payment_id>/', views.issue_refund, name='issue_refund'),
<<<<<<< HEAD
    path('refunds/', views.refund_list, name='refund_list'),  # Optional: general refunds list page
    path('refunds/request/', views.create_refund_request, name='create_refund_request'),
    path('refund/request/<int:payment_id>/', views.request_refund, name='request_refund'),
    path('billing-history/<int:pk>/', views.patient_billing_history, name='patient_billing_history'),
    path('invoice/record/', views.record_billing, name='record_billing'), 

    
=======
    path('refunds/', views.refund_list, name='refund_list'),
    path('refunds/request/', views.create_refund_request, name='create_refund_request'),
    path('refund/request/<int:payment_id>/', views.request_refund, name='request_refund'),

    # Patient billing
    path('billing-history/<int:pk>/', views.patient_billing_history, name='patient_billing_history'),
    path('invoice/record/', views.record_billing, name='record_billing'),
    path('generate-reference-number/', views.generate_reference_number, name='generate_reference_number'),
    path('patients/', views.patient_list, name='patient_list'),
    path('ajax/patient-billing-info/', get_patient_billing_info, name='patient_billing_info'),

    # Reports (HTML views)
    path('reports/daily/', views.daily_report, name='daily_report'),
    path('reports/monthly/', views.monthly_report, name='monthly_report'),

    # CSV export
    path('reports/export/csv/', views.export_csv, name='export_csv'),

    # PDF export menu page
    path('reports/export/pdf/', views.export_pdf, name='export_pdf'),

    # Actual PDF generators
    path('reports/export/daily-pdf/', views.export_daily_pdf, name='export_daily_pdf'),
    path('reports/export/monthly-pdf/', views.export_monthly_pdf, name='export_monthly_pdf'),
    path('notes/add/', views.add_account_note, name='add_account_note'),
    path('notes/<int:note_id>/toggle-pin/', views.toggle_account_note_pin, name='toggle_account_note_pin'),
    path('patient/<int:patient_id>/add-note/', views.add_patient_note, name='add_patient_note'),

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
]
