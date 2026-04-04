from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.shortcuts import render,redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from core.decorators import cashier_required
from .forms import PaymentForm,AccountNoteForm
from .models import  Payment, Invoice,InvoiceItem,Payment,Alert,DashboardSection,AccountNote
from .forms import InvoiceForm
from django.utils import timezone
from .models import Refund,Currency,AuditLog
from .forms import RefundForm
import uuid
from django.views.decorators.http import require_GET
import random
import datetime
import json
from cashier.models import Refund
from core.models import RefundRequest,PatientNote
from django.conf import settings
from core.forms import RefundRequestForm 
from django.contrib import messages
from core.models import Patient 
from core.decorators import cashier_or_admin_required
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import Count, Q,ExpressionWrapper,F,DecimalField
from core.models import Appointment
from django.db.models.functions import Coalesce
from django.db.models import Sum, Value, DecimalField
from datetime import timedelta
from django.utils.dateparse import parse_date
from cashier.models import Alert
from django.core.management import call_command
import logging
from admin_panel.models import PaymentModeReport 
from datetime import date
from django.views.decorators.http import require_POST
import csv
import datetime
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from xhtml2pdf import pisa
from core.models import PatientAccountNote
from core.utils import log_audit_action
from .models import UserSessionLog


def is_cashier(user):
    return user.is_authenticated and user.role == 'cashier'

@cashier_required
def cashier_dashboard(request):
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    start_of_month = today.replace(day=1)

    # Payments aggregation
    total_collected_today = Payment.objects.filter(
        date_received__date=today,
        amount__gt=0
    ).aggregate(total=Coalesce(Sum('amount'), Value(0, output_field=DecimalField())))['total']

    total_collected_week = Payment.objects.filter(
        date_received__date__gte=start_of_week,
        amount__gt=0
    ).aggregate(total=Coalesce(Sum('amount'), Value(0, output_field=DecimalField())))['total']

    total_collected_month = Payment.objects.filter(
        date_received__date__gte=start_of_month,
        amount__gt=0
    ).aggregate(total=Coalesce(Sum('amount'), Value(0, output_field=DecimalField())))['total']

    # Outstanding invoices
    total_outstanding = Invoice.objects.filter(
        payment_status__in=['unpaid', 'partial'],
        status='approved'
    ).aggregate(
        total=Coalesce(
            Sum('total_due') - Sum('amount_paid'),
            Value(0),
            output_field=DecimalField()
        )
    )['total']

    payments_processed = Payment.objects.filter(amount__gt=0).count()
    pending_invoices = Invoice.objects.filter(status='pending').count()

    total_refunds = Refund.objects.filter(is_approved=True).aggregate(
        total=Coalesce(Sum('refund_amount'), Value(0, output_field=DecimalField()))
    )['total']

    # Latest payments and invoices
    payments = Payment.objects.select_related('received_by').order_by('-date_received')[:10]
    invoices = Invoice.objects.order_by('-date_generated')[:10]

    # ✅ FIX: Use -id instead of -created_at for reliability
    alerts = Alert.objects.filter(is_resolved=False).order_by('-id')[:10]

    # Patients with aggregate financial info
    patients = Patient.objects.all().annotate(
        total_invoices=Coalesce(
            Sum('invoices__total_due'),
            Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))
        ),
        total_payments=Coalesce(
            Sum('payments__amount'),
            Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))
        ),
    ).annotate(
        outstanding_balance=ExpressionWrapper(
            F('total_invoices') - F('total_payments'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        invoice_count=Count('invoices', distinct=True),
        total_paid=F('total_payments'),
    )
    
    note_form = AccountNoteForm()
    recent_notes = PatientNote.objects.select_related('patient', 'created_by').order_by('-is_pinned', '-created_at')[:10]

    # fetch currencies (base + others)
    currencies = Currency.objects.all().order_by('-is_base', 'code')

    payments_total = Payment.objects.aggregate(
        total=Coalesce(Sum('amount'), Value(0, output_field=DecimalField()))
    )['total']

    invoice_total = Invoice.objects.aggregate(
        total=Coalesce(Sum('total_due'), Value(0, output_field=DecimalField()))
    )['total']

    total_collected_all_time = (payments_total or 0)
    total_revenue = total_collected_all_time

    refunds = Refund.objects.select_related('payment', 'issued_by') \
                        .order_by('-issue_date')  # no status filter
    

    # --- Insurance vs Out-of-Pocket totals ---
    insurance_total = Payment.objects.filter(
        payment_method__iexact='insurance',
        amount__gt=0
    ).aggregate(
        total=Coalesce(Sum('amount'), Value(0, output_field=DecimalField()))
    )['total'] or 0

    # Reuse your total_collected_all_time if already computed; otherwise compute it here
    if 'total_collected_all_time' not in locals():
        total_collected_all_time = Payment.objects.aggregate(
            total=Coalesce(Sum('amount'), Value(0, output_field=DecimalField()))
        )['total'] or 0

    out_of_pocket_total = (total_collected_all_time or 0) - (insurance_total or 0)

    recent_insurance_payments = Payment.objects.filter(
        payment_method__iexact='insurance'
    ).order_by('-date_received')[:10]

    patient_notes = PatientAccountNote.objects.select_related('patient', 'created_by')[:10]  # latest 10

    # Editable dashboard section (from admin)
    insurance_section = DashboardSection.objects.filter(
        key='insurance_payer_info',
        is_active=True
    ).first()

    exchange_rates = getattr(settings, "EXCHANGE_RATES", {})

    payment_modes = PaymentModeReport.objects.filter(is_active=True)

    summary = []
    for mode in payment_modes:
        total = Payment.objects.filter(payment_method=mode.name).aggregate(
            Sum('amount')
        )['amount__sum'] or 0

        summary.append({
            'mode': mode.name.replace('_', ' ').capitalize(),
            'total': total
        })

    # Forms + data for the notes section
    note_form = AccountNoteForm()
    recent_notes = PatientNote.objects.select_related('patient', 'created_by') \
    .order_by('-is_pinned', '-created_at')[:10]

    patient_notes = recent_notes

    logs = AuditLog.objects.select_related('user').all()[:20]  # last 20 actions
    recent_sessions = UserSessionLog.objects.select_related("user").order_by("-login_time")[:10]

    context = {
        'payments': payments,
        'invoices': invoices,
        'refunds': refunds,
        'patients': patients,
        'total_collected_today': total_collected_today,
        'total_collected_week': total_collected_week,
        'total_collected_month': total_collected_month,
        'total_outstanding': total_outstanding,
        'payments_processed': payments_processed,
        'pending_invoices': pending_invoices,
        'total_refunds': abs(total_refunds or 0),
        'total_collected_all_time': total_collected_all_time,
        'total_revenue': total_revenue,
        'alerts': alerts,
        'payment_summary': summary,
        'today': date.today(),
        'insurance_total': insurance_total,
        'out_of_pocket_total': out_of_pocket_total,
        'recent_insurance_payments': recent_insurance_payments,
        'insurance_section': insurance_section,
        'note_form': note_form,
        'recent_notes': recent_notes,
        'patient_notes': patient_notes,
        "currencies": currencies,
        'exchange_rates': exchange_rates,
        'audit_logs': logs,
        "recent_sessions": recent_sessions,
    }

    return render(request, 'cashier/dashboard.html', context)


@login_required  # or @cashier_required if you have it
def record_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user

            if payment.patient:
                payment.patient_name = payment.patient.full_name
            else:
                payment.patient_name = 'UNKNOWN'

            payment.save()

            # ✅ Log the payment action
            log_audit_action(
                user=request.user,
                action="Payment Recorded",
                model="Payment",
                object_id=payment.id,
                description=f"Payment of {payment.amount} recorded for patient {payment.patient_name}"
            )

            return redirect('cashier:cashier_payment_list')
    else:
        form = PaymentForm()

    return render(request, 'cashier/record_payment.html', {'form': form})


@cashier_or_admin_required
def payment_list(request):
    payments = Payment.objects.all().order_by('-date_received')
    return render(request, 'cashier/payment_list.html', {'payments': payments})



def generate_unique_invoice_number():
    today = timezone.now().strftime('%Y%m%d')
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"INV-{today}-{unique_suffix}"


@login_required
@cashier_required
def generate_invoice(request):
    if request.method == 'POST':
        data = request.POST

        # Parse JSON items safely
        try:
            items_data = json.loads(data.get('items_json', '[]'))
        except json.JSONDecodeError:
            items_data = []

        # Get patient
        patient_id = data.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)

        # Parse discount safely
        try:
            discount = float(data.get('discount', 0))
        except (ValueError, TypeError):
            discount = 0

        # Calculate subtotal and total_due
        subtotal = sum(float(item.get('amount', 0)) for item in items_data)
        total_due = max(subtotal - discount, 0)

        # Convert string dates to datetime.date
        try:
            service_date = datetime.datetime.strptime(data['service_date'], '%Y-%m-%d').date()
            due_date = datetime.datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            invoice_date = datetime.datetime.strptime(data['invoice_date'], '%Y-%m-%d').date()
        except (ValueError, KeyError):
            # Fallback to today if parsing fails
            service_date = due_date = invoice_date = datetime.date.today()

        # Create invoice
        invoice = Invoice.objects.create(
            patient=patient,
            service_date=service_date,
            due_date=due_date,
            invoice_date=invoice_date,
            service_type='others',
            subtotal=subtotal,
            discount=discount,
            total_due=total_due,
            invoice_number=generate_unique_invoice_number(),
            description=data.get('description', ''),
            generated_by=request.user,
        )

        # Create invoice items
        for item in items_data:
            amount = float(item.get('amount', 0))
            InvoiceItem.objects.create(
                invoice=invoice,
                description=item.get('description', ''),
                amount=amount
            )

        # Log audit action
        log_audit_action(
            user=request.user,
            action="GENERATE",
            model="Invoice",
            object_id=invoice.id,
            description=f"Invoice {invoice.invoice_number} generated for patient {patient.full_name}"
        )

        return redirect('cashier:cashier_invoice_list')

    # GET request: show form with patients
    patients = Patient.objects.all()
    return render(request, 'cashier/generate_invoice.html', {'patients': patients})

@cashier_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()  # Related name from InvoiceItem model
    return render(request, 'cashier/invoice_detail.html', {
        'invoice': invoice,
        'items': items,
    })


@cashier_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('patient__user').order_by('-date_generated')
    alerts = Alert.objects.filter(is_resolved=False).order_by('-created_at')[:10]  # get latest unresolved alerts

    context = {
        'invoices': invoices,
        'alerts': alerts,
    }
    return render(request, 'cashier/invoice_list.html', context)


@cashier_required
def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('cashier:cashier_invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'cashier/edit_invoice.html', {'form': form, 'invoice': invoice})

@cashier_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        invoice.delete()
        return redirect('cashier:cashier_invoice_list')
    return render(request, 'cashier/delete_invoice.html', {'invoice': invoice})

@cashier_required
def print_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'cashier/print_invoice.html', {'invoice': invoice})


@cashier_required
def issue_refund(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.payment = payment
            refund.issued_by = request.user
            refund.save()
            return redirect('cashier:cashier_dashboard')
    else:
        form = RefundForm()

    return render(request, 'cashier/issue_refund.html', {
        'payment': payment,
        'form': form
    })


@cashier_required
def refund_list(request):
    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.issued_by = request.user
            refund.save()
            return redirect('cashier:refund_list')
    else:
        form = RefundForm()

    refunds = Refund.objects.select_related('payment').order_by('-issue_date')
    return render(request, 'cashier/refund_list.html', {
        'refunds': refunds,
        'form': form
    })

@login_required
def request_refund(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            refund_request = form.save(commit=False)
            refund_request.payment = payment                    # 🔧 Set the payment manually
            refund_request.issued_by = request.user             # 🔧 Set the cashier user
            refund_request.save()
            return redirect('cashier:cashier_dashboard')  # or wherever
    else:
        form = RefundRequestForm()

    return render(request, 'cashier/request_refund.html', {'form': form, 'payment': payment})





logger = logging.getLogger(__name__)

@login_required
def create_refund_request(request, payment_id):
    # Force payment to exist
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.payment = payment
            refund.issued_by = request.user
            refund.approval_status = 'Pending'
            refund.save()

            logger.info(f"Refund #{refund.id} created for {payment.patient_name} by {request.user.username} ({request.user.role})")
            messages.success(request, f"Refund request for {payment.patient_name} submitted successfully.")
            return redirect('cashier:refund_list')
        else:
            logger.warning(f"Refund form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = RefundRequestForm()

    return render(request, 'cashier/create_refund_request.html', {
        'form': form,
        'payment': payment
    })



def patient_billing_history(request, pk):
    patient = get_object_or_404(Patient, id=pk)
    invoices = Invoice.objects.filter(patient_id=pk).order_by('-invoice_date')
    payments = Payment.objects.filter(patient=patient).order_by('-date_received')
    
    total_invoiced = sum(invoice.total_due for invoice in invoices)  # ✅ use total_due not total_amount
    total_paid = sum(payment.amount for payment in payments)
    balance = total_invoiced - total_paid

    context = {
        'patient': patient,
        'invoices': invoices,
        'payments': payments,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'balance': balance,
    }
    return render(request, 'cashier/patient_billing_history.html', context)

@cashier_required
def record_billing(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)

        if form.is_valid():
            invoice = form.save(commit=False)

            # Parse items_json from form (if provided)
            try:
                items_data = json.loads(request.POST.get('items_json', '[]'))
            except json.JSONDecodeError:
                items_data = []

            # Calculate subtotal from items
            subtotal = sum(float(item.get('amount', 0)) for item in items_data)

            # Parse discount
            try:
                discount = float(request.POST.get('discount', 0))
            except (ValueError, TypeError):
                discount = 0

            # Calculate total_due (subtotal minus discount, never negative)
            total_due = max(subtotal - discount, 0)

            # Generate unique invoice number if not provided
            if not invoice.invoice_number:
                today_str = datetime.date.today().strftime('%Y%m%d')
                random_num = random.randint(1000, 9999)
                invoice.invoice_number = f"INV{today_str}{random_num}"

            # Set calculated values
            invoice.subtotal = subtotal
            invoice.discount = discount
            invoice.total_due = total_due
            invoice.generated_by = request.user
            invoice.save()

            # Save invoice items
            for item in items_data:
                amount = float(item.get('amount', 0))
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item.get('description', ''),
                    amount=amount
                )

            # --- Audit logging ---
            log_audit_action(
                user=request.user,
                action="Invoice Generated",
                model="Invoice",
                object_id=invoice.id,
                description=f"Invoice #{invoice.invoice_number} generated with total {total_due}"
            )

            return redirect('cashier:cashier_invoice_list')

    else:
        form = InvoiceForm()

    return render(request, 'cashier/record_billing.html', {'form': form})


@login_required
def generate_reference_number(request):
    if request.method == 'GET':
        style = 1  # Or make this dynamic if you want
        ref = Payment().generate_reference_number(style=style)

        # Ensure uniqueness
        while Payment.objects.filter(reference_number=ref).exists():
            ref = Payment().generate_reference_number(style=style)

        return JsonResponse({'reference_number': ref})
    
def patient_list(request):
    search_query = request.GET.get('search', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payment_method = request.GET.get('payment_method')  # match form field name
    payment_status = request.GET.get('payment_status')  # 'paid', 'unpaid', or None
    outstanding_filter = request.GET.get('outstanding')  # 'yes' or 'no'

    patients = Patient.objects.all()

    if search_query:
        patients = patients.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(invoices__invoice_number__icontains=search_query)
        ).distinct()

    if start_date:
        start = parse_date(start_date)
        if start:
            patients = patients.filter(
                Q(payments__date_received__gte=start) |
                Q(invoices__invoice_date__gte=start)
            ).distinct()

    if end_date:
        end = parse_date(end_date)
        if end:
            patients = patients.filter(
                Q(payments__date_received__lte=end) |
                Q(invoices__invoice_date__lte=end)
            ).distinct()

    if payment_method:
        patients = patients.filter(payments__payment_method=payment_method).distinct()

    if payment_status == 'paid':
        # Filter patients having invoices approved (paid)
        patients = patients.filter(invoices__status='approved').distinct()
    elif payment_status == 'unpaid':
        # Filter patients having invoices pending (unpaid)
        patients = patients.filter(invoices__status='pending').distinct()

    # Annotate totals and calculate outstanding balance safely
    patients = patients.annotate(
        total_invoices=Coalesce(
            Sum('invoices__total_due'),
            Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))
        ),
        total_payments=Coalesce(
            Sum('payments__amount'),
            Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))
        ),
    ).annotate(
        outstanding_balance=ExpressionWrapper(
            F('total_invoices') - F('total_payments'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).annotate(
        invoice_count=Count('invoices', distinct=True),
        total_paid=Sum('payments__amount', distinct=True),
    )

    if outstanding_filter == 'yes':
        patients = patients.filter(outstanding_balance__gt=0)
    elif outstanding_filter == 'no':
        patients = patients.filter(outstanding_balance__lte=0)

    context = {
        'patients': patients,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'payment_method': payment_method,
        'payment_status': payment_status,
        'outstanding_filter': outstanding_filter,
    }
    return render(request, 'cashier/patient_list.html', context)

@require_GET
@login_required
def get_patient_billing_info(request):
    patient_id = request.GET.get('patient_id')
    if not patient_id:
        return JsonResponse({'error': 'No patient ID provided'}, status=400)

    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)

    invoices = Invoice.objects.filter(patient=patient)
    payments = Payment.objects.filter(patient=patient)

    total_invoiced = invoices.aggregate(total=Coalesce(Sum('total_due'), 0))['total']
    total_paid = payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
    outstanding = total_invoiced - total_paid

    return JsonResponse({
        'total_invoiced': float(total_invoiced or 0),
        'total_paid': float(total_paid or 0),
        'outstanding': float(outstanding or 0),
    })


def daily_report(request):
    today = datetime.date.today()
    payments = Payment.objects.filter(date_received__date=today)
    return render(request, 'cashier/reports/daily_report.html', {'payments': payments})


def monthly_report(request):
    now = datetime.date.today()
    payments = Payment.objects.filter(
        date_received__month=now.month,
        date_received__year=now.year
    )
    return render(request, 'cashier/reports/monthly_report.html', {'payments': payments})

def export_csv(request):
    # CSV export
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'
    writer = csv.writer(response)
    writer.writerow(['Patient', 'Amount', 'Payment Mode', 'Date'])
    for payment in Payment.objects.all():
        writer.writerow([payment.patient_name, payment.amount, payment.payment_method, payment.date_received])
    return response

def export_pdf(request):
    # Show export options
    return render(request, 'cashier/reports/export_options.html')

def export_daily_pdf(request):
    today = datetime.date.today()
    payments = Payment.objects.filter(date_received__date=today)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="daily_report_{today}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Daily Payments Report - {today}")

    y = height - 100
    p.setFont("Helvetica", 12)
    for payment in payments:
        line = f"{payment.patient_name} | ₦{payment.amount:.2f} | {payment.payment_method} | {payment.date_received}"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = height - 50

    p.showPage()
    p.save()
    return response


def export_monthly_pdf(request):
    now = datetime.date.today()
    payments = Payment.objects.filter(
        date_received__month=now.month,
        date_received__year=now.year
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="monthly_report_{now.strftime('%Y_%m')}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Monthly Payments Report - {now.strftime('%B %Y')}")

    y = height - 100
    p.setFont("Helvetica", 12)
    for payment in payments:
        line = f"{payment.patient_name} | ₦{payment.amount:.2f} | {payment.payment_method} | {payment.date_received}"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = height - 50

    p.showPage()
    p.save()
    return response

def render_to_pdf(template_src, context_dict={}):
    """Helper function to render HTML template to PDF."""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return HttpResponse('PDF generation failed', status=500)
    return result


def export_daily_pdf(request):
    """Generate PDF for today's payments."""
    today = datetime.date.today()
    payments = Payment.objects.filter(date_received__date=today)
    context = {'payments': payments}
    return render_to_pdf('cashier/reports/daily_report.html', context)


def export_monthly_pdf(request):
    """Generate PDF for this month's payments."""
    now = datetime.date.today()
    payments = Payment.objects.filter(
        date_received__month=now.month,
        date_received__year=now.year
    )
    context = {'payments': payments}
    return render_to_pdf('cashier/reports/monthly_report.html', context)


# --- toggle pin ---
@cashier_required
def toggle_account_note_pin(request, note_id):
    note = get_object_or_404(PatientNote, id=note_id)
    note.is_pinned = not note.is_pinned
    note.save(update_fields=['is_pinned'])

    # ✅ Audit log
    action = "PINNED" if note.is_pinned else "UNPINNED"
    log_audit_action(
        user=request.user,
        action=action,
        model="PatientNote",
        object_id=str(note.id),
        description=f"{action} note for patient {note.patient}"
    )

    return redirect('cashier:cashier_dashboard')




@login_required
def add_account_note(request):
    if request.method == "POST":
        form = AccountNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.created_by = request.user
            note.save()
            messages.success(request, "Account note added successfully.")
            return redirect('cashier:cashier_dashboard')  # adjust if your dashboard URL name is different
    else:
        form = AccountNoteForm()
    return render(request, 'cashier/add_account_note.html', {'form': form})


@login_required
def add_patient_note(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == "POST":
        note_text = request.POST.get("note")
        if note_text:
            latest_invoice = Invoice.objects.filter(patient=patient).order_by('-date_generated').first()

            note = PatientNote.objects.create(
                patient=patient,
                created_by=request.user,
                note=note_text,
                invoice=latest_invoice
            )

            # ✅ Audit log
            log_audit_action(
                user=request.user,
                action="CREATE",
                model="PatientNote",
                object_id=str(note.id),
                description=f"Added note for {patient}"
            )

        return redirect('cashier:cashier_dashboard')

    return render(request, "cashier/add_note.html", {"patient": patient})
