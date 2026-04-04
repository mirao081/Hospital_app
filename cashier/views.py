from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.shortcuts import render,redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from core.decorators import cashier_required
from .forms import PaymentForm
from .models import Payment
from .models import Invoice,InvoiceItem
from .forms import InvoiceForm
from django.utils import timezone
from .models import Refund
from .forms import RefundForm
import uuid
import json
from cashier.models import Refund
from core.models import RefundRequest

from core.forms import RefundRequestForm 
from django.contrib import messages
from core.models import Patient 
from core.decorators import cashier_or_admin_required




def is_cashier(user):
    return user.is_authenticated and user.role == 'cashier'


@cashier_required
def cashier_dashboard(request):
    payments = Payment.objects.select_related('received_by').order_by('-date_received')[:10]
    invoices = Invoice.objects.order_by('-date_generated')[:5]
    patients = Patient.objects.all()

    # ✅ Fetch ALL refund requests, ordered from most recent to oldest
    refunds = RefundRequest.objects.select_related('payment', 'issued_by') \
                                   .order_by('-created_at')

    return render(request, 'cashier/dashboard.html', {
        'payments': payments,
        'invoices': invoices,
        'refunds': refunds,  # used in the "Recent Refunds & Adjustments" table
        'patients': patients,
    })

@cashier_required
def record_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user

            print("📌 Cleaned data:", form.cleaned_data)
            print("📌 Patient:", payment.patient)
            print("📌 Patient full_name:", getattr(payment.patient, 'full_name', 'N/A'))

            # Set patient_name from full_name
            if payment.patient:
                payment.patient_name = payment.patient.full_name
            else:
                payment.patient_name = 'UNKNOWN'

            print("📌 Assigned patient_name:", payment.patient_name)

            payment.save()
            return redirect('cashier:cashier_payment_list')
        else:
            print("❌ Form is invalid:", form.errors)
    else:
        form = PaymentForm()

    return render(request, 'cashier/record_payment.html', {'form': form})

@cashier_or_admin_required
def payment_list(request):
    payments = Payment.objects.all().order_by('-date_received')
    return render(request, 'cashier/payment_list.html', {'payments': payments})


def is_cashier(user):
    return user.is_authenticated and user.role == 'cashier'



def generate_unique_invoice_number():
    today = timezone.now().strftime('%Y%m%d')
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"INV-{today}-{unique_suffix}"

@cashier_required
def generate_invoice(request):
    if request.method == 'POST':
        data = request.POST
        items_data = json.loads(data.get('items_json'))

        # ✅ Get the actual Patient object
        patient_id = data.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)

        # Parse discount safely as float
        try:
            discount = float(data.get('discount', 0))
        except (ValueError, TypeError):
            discount = 0

        invoice = Invoice.objects.create(
            patient=patient,
            service_date=data['service_date'],
            service_type='others',
            subtotal=0,
            discount=discount,
            total_due=0,
            due_date=data['due_date'],
            invoice_number=generate_unique_invoice_number(),
            invoice_date=data['invoice_date'],
            description=data.get('description', ''),
            generated_by=request.user,
        )

        subtotal = 0
        for item in items_data:
            amount = float(item.get('amount', 0))
            InvoiceItem.objects.create(
                invoice=invoice,
                description=item['description'],
                amount=amount
            )
            subtotal += amount

        invoice.subtotal = subtotal
        invoice.total_due = max(subtotal - discount, 0)
        invoice.save()

        return redirect('cashier:cashier_invoice_list')

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
    return render(request, 'cashier/invoice_list.html', {'invoices': invoices})



@cashier_required
def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('cashier_invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'cashier/edit_invoice.html', {'form': form, 'invoice': invoice})

@cashier_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        invoice.delete()
        return redirect('cashier_invoice_list')
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
            return redirect('cashier_dashboard')
    else:
        form = RefundForm()

    return render(request, 'cashier/issue_refund.html', {
        'payment': payment,
        'form': form
    })


@cashier_required
def refund_list(request):
    refunds = Refund.objects.select_related('payment', 'issued_by').order_by('-issue_date')
    return render(request, 'cashier/refund_list.html', {'refunds': refunds})

def refund_list(request):
    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.issued_by = request.user
            refund.save()
            return redirect('cashier:refund_list')  # reload page after submission
    else:
        form = RefundForm()

    refunds = Refund.objects.select_related('payment').order_by('-issue_date')
    return render(request, 'cashier/refund_list.html', {'refunds': refunds, 'form': form})


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
            return redirect('cashier_dashboard')  # or wherever
    else:
        form = RefundRequestForm()

    return render(request, 'cashier/request_refund.html', {'form': form, 'payment': payment})


@login_required
def create_refund_request(request):
    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.issued_by = request.user
            refund.save()
            messages.success(request, "Refund request submitted successfully.")
            return redirect('refund_approval_list')  # Update to your actual redirect
    else:
        form = RefundRequestForm()

    return render(request, 'cashier/create_refund_request.html', {'form': form})


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

@login_required
def record_billing(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.generated_by = request.user
            invoice.save()
            return redirect('cashier:cashier_dashboard')
    else:
        form = InvoiceForm()
    
    return render(request, 'cashier/record_billing.html', {'form': form})