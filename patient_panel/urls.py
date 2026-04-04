from django.urls import path
from . import views

app_name = "patient_panel"

urlpatterns = [
    path('', views.patient_dashboard, name='patient_dashboard'),
    path('submit-survey/', views.submit_survey, name='submit_survey'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
]
