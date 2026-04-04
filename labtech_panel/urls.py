from django.urls import path
from . import views

app_name = "labtech_panel"

urlpatterns = [
    path('', views.labtech_dashboard, name='labtech_dashboard'),
    path('lab-report/<int:pk>/print/', views.print_lab_report, name='print_lab_report'),
    path('lab-report/<int:pk>/pdf/', views.download_lab_pdf, name='download_lab_pdf'),
]
