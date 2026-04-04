from django.urls import path
from . import views
from .views import (
    landing_page, terms_view, privacy_policy_view,assign_bed_view 
)


urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.custom_login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.role_based_redirect_view, name='role_redirect'),
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('blogs/', views.blogs_view, name='blogs'), 
    path('book-footer-appointment/', views.footer_appointment, name='footer_appointment'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy-policy/', privacy_policy_view, name='privacy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('doctors/', views.doctors_page, name='doctors'),
    path('blogs/', views.blogs_view, name='blogs'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),  # Optional for detailed view
    # path('blogs/', views.blog_highlight_section, name='blogs'),
    path('departments/', views.departments_view, name='departments'),
    path('departments/<int:department_id>/doctors/', views.doctors_by_department, name='doctors_by_department'),
    path('appointment/', views.appointment_view, name='appointment'),
    path('testimonials/', views.testimonials_view, name='testimonials'),
    path('contact/', views.contact_view, name='contact'),
    path('appointment/success/', views.success_page, name='success_page'),
    path('assign-bed/', assign_bed_view, name='assign_bed'),
    path('unassign-bed/<int:bed_id>/', views.unassign_bed_view, name='unassign_bed'),
     path('admin/access-logs/', views.admin_access_logs, name='admin_access_logs'),
    path('admin/failed-logins/', views.admin_failed_logins, name='admin_failed_logins'),

    
]



