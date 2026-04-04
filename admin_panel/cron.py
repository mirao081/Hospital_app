from django_cron import CronJobBase, Schedule
from admin_panel.utils.metrics import (
    update_readmission_rate,
    update_infection_rate,
    update_outcome_trend,
)

class UpdateClinicalMetricsCronJob(CronJobBase):
    RUN_EVERY_MINS = 60 * 24  # daily

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'admin_panel.update_clinical_metrics'

    def do(self):
        update_readmission_rate()
        update_infection_rate()
        update_outcome_trend()
