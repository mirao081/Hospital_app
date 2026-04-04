from django.urls import path
from . import views

app_name = "nurse_panel"

urlpatterns = [
    path('', views.nurse_dashboard, name='nurse_dashboard'),
    path('patients/', views.nurse_patient_list, name='nurse_patient_list'),
    path('patients/add/', views.add_nurse_patient, name='add_nurse_patient'),
    path('patients/<int:patient_id>/', views.nurse_patient_detail, name='nurse_patient_detail'),
    path('add-vitals/<int:patient_id>/', views.add_vitals, name='add_vitals'),
    path('log-round/', views.log_daily_round, name='log_daily_round'),
    path('reminders/', views.view_reminders, name='view_reminders'),
    path('tasks/', views.nurse_task_list, name='nurse_task_list'),
    

]
