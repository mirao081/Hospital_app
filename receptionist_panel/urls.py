from django.urls import path
from . import views

app_name = "receptionist"

urlpatterns = [
    path('', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('register-patient/', views.register_patient, name='register_patient'),
    path('schedule-appointment/', views.schedule_appointment, name='schedule_appointment'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('messages/', views.send_internal_message, name='send_internal_message'),
    path('onboarding/', views.patient_onboarding, name='patient_onboarding'),
    path('service-guidelines/', views.service_guidelines, name='service_guidelines'),
]
