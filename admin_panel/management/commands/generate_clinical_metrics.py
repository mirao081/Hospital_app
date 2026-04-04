# admin_panel/management/commands/generate_clinical_metrics.py
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from admin_panel.utils.metrics import (
    update_readmission_rate,
    update_outcome_trend,
    update_infection_rate
)

class Command(BaseCommand):
    help = 'Generates and updates clinical quality metrics'

    def handle(self, *args, **kwargs):
        update_readmission_rate()
        update_outcome_trend()
        update_infection_rate()
        self.stdout.write(self.style.SUCCESS('✅ Clinical metrics updated successfully.'))

        log_file = os.path.join(os.path.dirname(__file__), 'metrics_log.txt')
        with open(log_file, 'a') as f:
            f.write(f"[{datetime.now()}] Clinical metrics updated successfully.\n")

