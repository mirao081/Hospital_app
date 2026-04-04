from django.urls import path
from . import views
from .views import doctor_dashboard

app_name = 'doctor_panel'

urlpatterns = [
    path('', views.doctor_dashboard, name='doctor_dashboard'),
    path('add-record/', views.add_medical_record, name='add_medical_record'),
    path('inbox/', views.doctor_inbox_view, name='inbox'),
    path('messages/<int:pk>/', views.message_detail_view, name='message_detail'),  # optional
]