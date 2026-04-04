# cashier/urls.py
from django.urls import path
from . import views


app_name = 'cashier'  # Enables namespaced URL resolution in templates

urlpatterns = [
    path('', views.cashier_dashboard),
    path('dashboard/', views.cashier_dashboard, name='cashier_dashboard'),
    path('record-payment/', views.record_payment, name='cashier_record_payment'),
    path('payments/', views.payment_list, name='cashier_payment_list'),
    path('generate-invoice/', views.generate_invoice, name='cashier_generate_invoice'),
    path('invoices/', views.invoice_list, name='cashier_invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/edit/', views.edit_invoice, name='edit_invoice'),
    path('invoices/<int:invoice_id>/delete/', views.delete_invoice, name='delete_invoice'),
    path('invoices/<int:invoice_id>/print/', views.print_invoice, name='print_invoice'),

    # Refund functionality
    path('refund/<int:payment_id>/', views.issue_refund, name='issue_refund'),
    path('refunds/', views.refund_list, name='refund_list'),  # Optional: general refunds list page
    path('refunds/request/', views.create_refund_request, name='create_refund_request'),
    path('refund/request/<int:payment_id>/', views.request_refund, name='request_refund'),
    path('billing-history/<int:pk>/', views.patient_billing_history, name='patient_billing_history'),
    path('invoice/record/', views.record_billing, name='record_billing'), 

    
]
