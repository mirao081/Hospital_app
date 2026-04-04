from django.contrib import admin
from .models import MedicalRecord, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'message', 'timestamp', 'read')
    list_filter = ('doctor', 'read', 'timestamp')
    search_fields = ('doctor__user__username', 'message')
    
admin.site.register(MedicalRecord)

# Register your models here.
