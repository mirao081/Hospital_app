from django.core.management.base import BaseCommand
from django.db.models import F, Q
from cashier.models import Alert, Invoice, Refund
from django.utils import timezone


class Command(BaseCommand):
    help = 'Generate alerts for cashier based on refunds, invoices, and discrepancies'

    def handle(self, *args, **kwargs):
        # -------------------------------
        # 1. Refund approvals
        # -------------------------------
        # Remove refund alerts ONLY for refunds that are no longer pending
        resolved_refund_ids = Refund.objects.exclude(
            Q(is_approved=False) | Q(is_approved__isnull=True)
        ).values_list('id', flat=True)

        Alert.objects.filter(
            alert_type='refund_approval',
            description__regex=r"Refund request #(\d+)",
            is_resolved=False
        ).filter(
            description__iregex=r"Refund request #(" + "|".join(map(str, resolved_refund_ids)) + ")"
        ).update(is_resolved=True)

        # Add alerts for refunds that are pending but not already alerted
        pending_refunds = Refund.objects.filter(
            Q(is_approved=False) | Q(is_approved__isnull=True)
        )

        for refund in pending_refunds:
            if not Alert.objects.filter(
                alert_type='refund_approval',
                description__icontains=f"Refund request #{refund.id}",
                is_resolved=False
            ).exists():
                Alert.objects.create(
                    alert_type='refund_approval',
                    description=f"Refund request #{refund.id} awaiting approval",
                    is_resolved=False,
                )

        # -------------------------------
        # 2. Large unpaid balances (> ₦50,000)
        # -------------------------------
        threshold = 50000
        invoices_with_balance = Invoice.objects.annotate(
            outstanding=F('total_due') - F('amount_paid')
        ).filter(outstanding__gt=threshold)

        # Resolve large balance alerts for invoices that are now below threshold
        Alert.objects.filter(
            alert_type='large_balance',
            is_resolved=False
        ).exclude(
            description__iregex=r"Patient .* has an outstanding balance of ₦(\d+(\.\d{1,2})?)"
        ).update(is_resolved=True)

        # Create new large balance alerts if not already present
        for invoice in invoices_with_balance:
            if not Alert.objects.filter(
                alert_type='large_balance',
                description__icontains=f"Patient {invoice.patient}",
                is_resolved=False
            ).exists():
                Alert.objects.create(
                    alert_type='large_balance',
                    description=f"Patient {invoice.patient} has an outstanding balance of ₦{invoice.total_due - invoice.amount_paid:.2f}",
                    is_resolved=False,
                )

        # -------------------------------
        # 3. Invoice discrepancies (overpaid)
        # -------------------------------
        discrepancy_invoices = Invoice.objects.filter(amount_paid__gt=F('total_due'))

        # Resolve discrepancy alerts that no longer apply
        Alert.objects.filter(
            alert_type='invoice_discrepancy',
            is_resolved=False
        ).exclude(
            description__icontains='has amount paid greater than total due'
        ).update(is_resolved=True)

        # Create alerts for discrepancies not already present
        for invoice in discrepancy_invoices:
            if not Alert.objects.filter(
                alert_type='invoice_discrepancy',
                description__icontains=f"Invoice {invoice.invoice_number}",
                is_resolved=False
            ).exists():
                Alert.objects.create(
                    alert_type='invoice_discrepancy',
                    description=f"Invoice {invoice.invoice_number} has amount paid greater than total due.",
                    is_resolved=False,
                )

        self.stdout.write(self.style.SUCCESS('Alerts generated/updated successfully.'))
