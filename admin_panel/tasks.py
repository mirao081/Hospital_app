# admin_panel/tasks.py
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta
from .models import (
    AutomationSettings, OverduePaymentRule, LowInventoryRule,
    ShiftSchedulingRule, AutomationLog
)
from cashier.models import Invoice
from core.models import InventoryItem, StaffProfile
from .sms_backend import send_sms

def is_automation_enabled():
    s = AutomationSettings.objects.first()
    return (s.enabled if s else True)


# --- 1. Overdue Payments ---
def run_overdue_payment_rules():
    if not is_automation_enabled():
        return "Automations disabled"

    rules = OverduePaymentRule.objects.filter(enabled=True)
    now = timezone.now().date()
    flagged_count = 0
    logs = []

    for rule in rules:
        cutoff_date = now - timedelta(days=rule.days_overdue)
        invoices = Invoice.objects.filter(
            status='pending',
            due_date__lte=cutoff_date,
            total_due__gte=rule.min_amount
        )

        for inv in invoices:
            inv.status = 'rejected'  # Or create a flag field if you prefer
            inv.description = (inv.description or "") + f"\n[FLAGGED] {rule.flag_reason}"
            inv.save(update_fields=['status', 'description'])
            flagged_count += 1

        logs.append(f"{rule.name}: flagged {invoices.count()} invoices")

    AutomationLog.objects.create(run_type='overdue', details="; ".join(logs), success=True)
    return {"flagged": flagged_count, "details": logs}


# --- 2. Low Inventory Alerts ---
def run_low_inventory_rules():
    if not is_automation_enabled():
        return "Automations disabled"

    rules = LowInventoryRule.objects.filter(enabled=True)
    alerts_sent = 0

    for rule in rules:
        items = InventoryItem.objects.filter(quantity__lte=rule.threshold)
        if not items.exists():
            continue

        subject = f"[Alert] Low inventory - {rule.name}"
        body = "Low inventory detected:\n\n" + "\n".join(
            f"{it.name}: qty={it.quantity} (threshold={rule.threshold})"
            for it in items
        )

        for email in rule.get_email_list():
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
            alerts_sent += 1

        for phone in rule.get_sms_list():
            send_sms(phone, body)
            alerts_sent += 1

        AutomationLog.objects.create(run_type='inventory', details=f"{rule.name} alerted {items.count()} items", success=True)

    return {"alerts_sent": alerts_sent}


# --- 3. Shift Scheduling ---
# admin_panel/tasks.py
def run_overdue_payment_rules():
    if not is_automation_enabled():
        return "Automations disabled"

    rules = OverduePaymentRule.objects.filter(enabled=True)
    now = timezone.now().date()
    flagged_count = 0
    logs = []

    for rule in rules:
        cutoff_date = now - timedelta(days=rule.days_overdue)
        invoices = Invoice.objects.filter(
            status='pending',
            due_date__lte=cutoff_date,
            total_due__gte=rule.min_amount,
            is_flagged=False
        )

        for inv in invoices:
            inv.is_flagged = True
            inv.description = (inv.description or "") + f"\n[FLAGGED] {rule.flag_reason}"
            inv.save(update_fields=['is_flagged', 'description'])
            flagged_count += 1

        logs.append(f"{rule.name}: flagged {invoices.count()} invoices")

    AutomationLog.objects.create(run_type='overdue', details="; ".join(logs), success=True)
    return {"flagged": flagged_count, "details": logs}

