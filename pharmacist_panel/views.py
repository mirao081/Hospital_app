
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta  # <- import timedelta here
from .models import Medicine, Prescription
from .forms import MedicineForm 
from datetime import date
from django.http import HttpResponse
from django.utils.timezone import datetime
import csv
from django.db.models import Q
from .models import DispensationRecord
from django.views.decorators.http import require_POST
from .models import ReturnedMedicine,WastageEntry
from django.http import HttpResponseBadRequest
from .models import Supplier, PurchaseOrder, SupplierInvoice
from cashier.models import Invoice
from .forms import PrescriptionForm
from core.models import InventoryItem
from django.db.models import F
from doctor_panel.utils import get_comm_context




@login_required
def pharmacist_dashboard(request):
    today = timezone.now().date()

    total_medicines = Medicine.objects.count()
    expiring_soon = Medicine.objects.filter(expiry_date__lte=today + timedelta(days=30)).count()
    out_of_stock = Medicine.objects.filter(stock=0).count()
    pending_prescriptions = Prescription.objects.filter(status='pending').count()
    medicines = Medicine.objects.all()
    prescriptions = Prescription.objects.all().order_by('-date')


    recent_fulfillments = Prescription.objects.filter(status='fulfilled').order_by('-date')[:5]
    alerts = (Medicine.objects.filter(stock__lte=5) | 
              Medicine.objects.filter(expiry_date__lte=today + timedelta(days=7))).distinct()

    context = {
        'total_medicines': total_medicines,
        'expiring_soon': expiring_soon,
        'out_of_stock': out_of_stock,
        'pending_prescriptions': pending_prescriptions,
        'recent_fulfillments': recent_fulfillments,
        'alerts': alerts,
        'today': today,
        'medicines': medicines,
        'prescriptions': prescriptions,

    }
    context.update(get_comm_context(request.user, scope="all", limit=5))

    return render(request, 'pharmacist_panel/dashboard.html', context)

@login_required
def add_medicine(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pharmacist_panel:dashboard')
    else:
        form = MedicineForm()
    return render(request, 'pharmacist_panel/add_medicine.html', {'form': form})


def todays_prescriptions(request):
    today = date.today()
    prescriptions = Prescription.objects.filter(date=today)
    return render(request, 'pharmacist_panel/todays_prescriptions.html', {
        'prescriptions': prescriptions,
        'today': today
    })

def edit_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)

    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully.')
            return redirect('pharmacist_panel:dashboard')  # Redirect to dashboard
    else:
        form = MedicineForm(instance=medicine)

    return render(request, 'pharmacist_panel/edit_medicine.html', {
        'form': form,
        'medicine': medicine
    })


def delete_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)

    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully.')
        return redirect('pharmacist_panel:dashboard')  # Redirect to dashboard

    return render(request, 'pharmacist_panel/delete_medicine.html', {
        'medicine': medicine
    })


def prescription_list(request):
    prescriptions = Prescription.objects.all()
    return render(request, 'pharmacist_panel/prescription_list.html', {
        'prescriptions': prescriptions
    })


def fulfill_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    prescription.status = 'fulfilled'
    prescription.save()
    return redirect('pharmacist_panel:dashboard')  # or wherever you want to redirect

def reject_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    prescription.status = 'rejected'  # You may need to add 'rejected' to STATUS_CHOICES
    prescription.save()
    return redirect('pharmacist_panel:dashboard')

def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'pharmacist_panel/medicine_list.html', {'medicines': medicines})


@login_required
def acknowledge_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)

    if prescription.status != 'fulfilled':
        prescription.status = 'fulfilled'
        prescription.save()
        message = f"Prescription for {prescription.patient_name} has been digitally acknowledged."
    else:
        message = f"Prescription for {prescription.patient_name} was already acknowledged."

    return HttpResponse(message)


def dispensation_records(request):
    query = DispensationRecord.objects.all().order_by('-date')

    # Filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    patient_name = request.GET.get('patient')

    if start_date:
        query = query.filter(date__date__gte=start_date)
    if end_date:
        query = query.filter(date__date__lte=end_date)
    if patient_name:
        query = query.filter(patient_name__icontains=patient_name)

    return render(request, 'pharmacist_panel/dispensation_records.html', {
        'records': query,
        'start_date': start_date,
        'end_date': end_date,
        'patient_name': patient_name
    })

def export_dispensation_csv(request):
    records = DispensationRecord.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dispensations.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Patient', 'Medicine', 'Quantity', 'Dispensed By'])
    for record in records:
        writer.writerow([
            record.date.strftime("%Y-%m-%d %H:%M"),
            record.patient_name,
            record.medicine.name,
            record.quantity,
            record.dispensed_by.get_full_name() if record.dispensed_by else ''
        ])
    return response

@login_required
def returns_wastage(request):
    tab = request.GET.get('tab', 'returns')
    returned_medicines = ReturnedMedicine.objects.all().order_by('-date')
    wastage_entries = WastageEntry.objects.all().order_by('-date')
    medicines = Medicine.objects.all().order_by('name')

    context = {
        'tab': tab,
        'returned_medicines': returned_medicines,
        'wastage_entries': wastage_entries,
        'medicines': medicines,
    }
    return render(request, 'pharmacist_panel/returns_wastage.html', context)
@require_POST
@login_required
def add_return_wastage(request):
    type = request.POST.get('type')
    medicine_id = request.POST.get('medicine')
    quantity = request.POST.get('quantity')
    note = request.POST.get('note')

    try:
        medicine = Medicine.objects.get(id=medicine_id)
    except Medicine.DoesNotExist:
        return HttpResponseBadRequest("Invalid medicine selected.")

    if type == 'return':
        ReturnedMedicine.objects.create(
            medicine=medicine,
            quantity=quantity,
            note=note,
            patient_or_ward="Ward or Patient Placeholder"  # Replace with actual input
        )
    elif type == 'wastage':
        WastageEntry.objects.create(
            medicine=medicine,
            quantity=quantity,
            note=note
        )

    return redirect('pharmacist_panel:returns_wastage')

def invoices_list(request):
    invoices = Invoice.objects.all().select_related('patient', 'generated_by').order_by('-date_generated')
    context = {
        'invoices': invoices,
    }
    return render(request, 'pharmacist_panel/invoices.html', context)


def suppliers_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'pharmacist_panel/suppliers.html', {'suppliers': suppliers})

def purchase_orders_list(request):
    purchase_orders = PurchaseOrder.objects.select_related('supplier').order_by('-order_date')
    return render(request, 'pharmacist_panel/purchase_orders.html', {'purchase_orders': purchase_orders})

def approve_supplier_invoices(request):
    invoices = SupplierInvoice.objects.filter(approved=False).select_related('purchase_order__supplier')
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        invoice = get_object_or_404(SupplierInvoice, id=invoice_id)
        invoice.approved = True
        invoice.approval_date = timezone.now()
        invoice.save()
        return redirect('pharmacist_panel:approve_supplier_invoices')
    return render(request, 'pharmacist_panel/approve_invoices.html', {'invoices': invoices})


# pharmacist_panel/views.py
@login_required
def create_prescription(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pharmacist_panel:dashboard')
    else:
        form = PrescriptionForm()
    
    return render(request, 'pharmacist_panel/create_prescription.html', {'form': form})

