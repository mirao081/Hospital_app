from django.urls import path
from . import views
from .views import (
    refund_approval_list,
    send_message,
    inbox_view,
    admin_dashboard,
    register_user,
    staff_checkin_checkout,
    staff_toggle_attendance,
    mark_message_read,
    message_detail_view,
    patient_engagement_view,
)

app_name = 'admin_panel'

urlpatterns = [
    path('', admin_dashboard, name='admin_dashboard'),

    # User registration
    path('register/', register_user, name='register_user'),

    # Staff attendance
    path('attendance/toggle/', staff_checkin_checkout, name='staff_checkin_checkout'),
    path('toggle-attendance/', staff_toggle_attendance, name='staff_toggle_attendance'),

    # Messages
    path('messages/read/<int:message_id>/', mark_message_read, name='mark_message_read'),
    path('inbox/', inbox_view, name='inbox'),
    path('enquiry/read/<int:enquiry_id>/', views.mark_enquiry_read, name='mark_enquiry_read'),
    path('inbox/<int:message_id>/', message_detail_view, name='message_detail'),
    path('messages/send/', send_message, name='send_message'),

    # Refunds
    path('refunds/', refund_approval_list, name='refund_approval_list'),
    path('refunds/<int:pk>/approve/', views.refund_approve, name='refund_approve'),

    # Self check-in/out (for logged-in staff)
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),

    # Admin-initiated check-in/out for other staff
    path('check-in/<int:user_id>/', views.check_in, name='check_in_by_id'),
    path('check-out/<int:user_id>/', views.check_out, name='check_out_by_id'),
    path('manual-checkin/', views.staff_manual_checkin, name='staff_manual_checkin'),

    # Clinical metrics & patient engagement
    path('clinical-metrics/', views.clinical_metrics_view, name='clinical_metrics'),
    path('patient-engagement/', patient_engagement_view, name='patient_engagement'),
    # urls.py
    path('refunds/', refund_approval_list, name='refund_approval_list'),  # List of refunds
    path('refunds/<int:pk>/approve/', views.refund_approve, name='refund_approve'),  # Approve/reject
    path('refund/<int:refund_id>/action/', views.refund_action, name='refund_action'),  # Optional generic action
     path('patient/<int:patient_id>/notes/', views.patient_notes, name='patient_notes'),
]
