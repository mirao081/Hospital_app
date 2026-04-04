"""
URL configuration for hospital_mgmt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from admin_panel.views import admin_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),

    # Dashboards
    path('dashboard/admin/', include(('admin_panel.urls', 'admin_panel'), namespace='admin_panel')),
    path('dashboard/doctor/', include(('doctor_panel.urls', 'doctor'), namespace='doctor')),
    path('dashboard/nurse/', include(('nurse_panel.urls', 'nurse'), namespace='nurse')),
    path('dashboard/receptionist/', include('receptionist_panel.urls')),
    path('pharmacist/', include(('pharmacist_panel.urls', 'pharmacist_panel'), namespace='pharmacist_panel')),
    path('dashboard/labtech/', include(('labtech_panel.urls', 'labtech'), namespace='labtech')),
    path('dashboard/patient/', include(('patient_panel.urls', 'patient'), namespace='patient')),
    path('cashier/', include(('cashier.urls', 'cashier'), namespace='cashier')),
    
]
    
    

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)