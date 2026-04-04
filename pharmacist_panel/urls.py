from django.urls import path
from . import views

app_name = "pharmacist_panel"

urlpatterns = [
    path('', views.pharmacist_dashboard, name='dashboard'),
    path('add-medicine/', views.add_medicine, name='add_medicine'),
    path('todays-prescriptions/', views.todays_prescriptions, name='todays_prescriptions'), 
    path('medicines/edit/<int:pk>/', views.edit_medicine, name='edit_medicine'),
    path('medicines/delete/<int:pk>/', views.delete_medicine, name='delete_medicine'),
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescription/<int:pk>/fulfill/', views.fulfill_prescription, name='fulfill_prescription'),
    path('prescription/<int:pk>/reject/', views.reject_prescription, name='reject_prescription'),
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('dispensations/', views.dispensation_records, name='dispensation_records'),
    path('dispensations/export/csv/', views.export_dispensation_csv, name='export_dispensation_csv'),
    path('returns-wastage/', views.returns_wastage, name='returns_wastage'),
    path('returns-wastage/add/', views.add_return_wastage, name='add_return_wastage'),
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('purchase-orders/', views.purchase_orders_list, name='purchase_orders_list'),
    path('approve-invoices/', views.approve_supplier_invoices, name='approve_supplier_invoices'),
    path('invoices/', views.invoices_list, name='invoices_list'),
    path('create-prescription/', views.create_prescription, name='create_prescription'),


]
