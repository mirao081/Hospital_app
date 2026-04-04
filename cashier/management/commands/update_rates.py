from django.core.management.base import BaseCommand
from cashier.services.exchange import fetch_exchange_rates

class Command(BaseCommand):
    help = "Fetch latest exchange rates from API"

    def handle(self, *args, **kwargs):
        try:
            fetch_exchange_rates()
            self.stdout.write(self.style.SUCCESS("✅ Exchange rates updated successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed: {e}"))
