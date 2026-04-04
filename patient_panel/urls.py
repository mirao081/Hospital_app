from django.urls import path
from . import views

app_name = "patient_panel"

urlpatterns = [
    path('', views.patient_dashboard, name='patient_dashboard'),
    path('submit-survey/', views.submit_survey, name='submit_survey'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
<<<<<<< HEAD
=======
    path("portal-request/", views.create_portal_request, name="create_portal_request"),
    path('create-request/', views.create_portal_request, name='create_portal_request'),
    path("portal-request/success/", views.portal_request_success, name="portal_request_success"),
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
]
