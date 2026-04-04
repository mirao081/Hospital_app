from django.core.management.base import BaseCommand
from core.models import Shift, Attendance
from datetime import date

class Command(BaseCommand):
    help = "Auto-create attendance records for staff scheduled today."

    def handle(self, *args, **kwargs):
        today = date.today()
        shifts_today = Shift.objects.filter(date=today)

        count = 0
        for shift in shifts_today:
            created, _ = Attendance.objects.get_or_create(
                staff=shift.staff,
                date=today,
                shift=shift,
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Initialized {count} attendance records for today."))
