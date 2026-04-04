# admin_panel/management/commands/run_automations.py
from django.core.management.base import BaseCommand
from admin_panel.tasks import (
    run_overdue_payment_rules, run_low_inventory_rules, run_shift_scheduling_rules
)

class Command(BaseCommand):
    help = 'Run all admin_panel automations'

    def handle(self, *args, **options):
        self.stdout.write("Running overdue payment rules...")
        self.stdout.write(str(run_overdue_payment_rules()))

        self.stdout.write("Running low inventory rules...")
        self.stdout.write(str(run_low_inventory_rules()))

        self.stdout.write("Running shift scheduling rules...")
        self.stdout.write(str(run_shift_scheduling_rules()))

        self.stdout.write(self.style.SUCCESS("Automations completed."))
