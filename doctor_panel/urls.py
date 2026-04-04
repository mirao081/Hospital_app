from django.urls import path
from . import views
from .views import doctor_dashboard

app_name = 'doctor_panel'

urlpatterns = [
    path('', views.doctor_dashboard, name='doctor_dashboard'),
    path('add-record/', views.add_medical_record, name='add_medical_record'),
<<<<<<< HEAD
    path('inbox/', views.doctor_inbox_view, name='inbox'),
    path('messages/<int:pk>/', views.message_detail_view, name='message_detail'),  # optional
=======
    path('inbox/', views.doctor_inbox_view, name='doctor_inbox'),
    path('enquiry/read/<int:enquiry_id>/', views.mark_enquiry_read, name='mark_enquiry_read'),
    path('messages/<int:pk>/', views.message_detail_view, name='message_detail'),  # optional
    path("record/<int:pk>/", views.view_record, name="view_record"),
    path("analytics/", views.doctor_analytics, name="doctor_analytics"),
    path("analytics/data/", views.doctor_analytics_data, name="doctor_analytics_data"),
    path("requests/<int:pk>/update/", views.update_request_status, name="update_request"),
    # doctor_panel/urls.py
    path('portal-request/<int:pk>/update/', views.update_request, name='update_request')



>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
]