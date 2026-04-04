from django.contrib import admin
from .models import Vitals, DailyRound, Reminder
from .models import MedicationOrder, MedicationLog, MedicationRequest


admin.site.register(Vitals)
admin.site.register(DailyRound)
admin.site.register(Reminder)
admin.site.register(MedicationOrder)
admin.site.register(MedicationLog)
admin.site.register(MedicationRequest)


# Register your models here.
