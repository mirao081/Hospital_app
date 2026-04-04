from django import forms
from .models import Payment
from .models import Invoice
<<<<<<< HEAD
from .models import Refund
from core.models import RefundRequest

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['patient', 'amount', 'payment_method', 'reference_number', 'remarks']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


=======
from .models import Refund,AccountNote
from core.models import RefundRequest


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'patient', 
            'amount', 
            'payment_method', 
            'service_type',  # added service_type here
            'reference_number', 
            'remarks'
        ]
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
<<<<<<< HEAD
            'patient',  # ForeignKey to Patient
            'service_date',
            'service_type',
            'subtotal',
            'total_due',
=======
            'patient',  
            'service_date',
            'service_type',
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
            'due_date',
            'invoice_number',
            'invoice_date',
            'description',
            'discount',
        ]
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
        }



class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['payment','refund_amount', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }


class RefundRequestForm(forms.ModelForm):
    class Meta:
<<<<<<< HEAD
        model = RefundRequest
        fields = ['refund_amount', 'reason']
=======
        model = RefundRequest  # corrected from Refund to RefundRequest
        fields = ['payment', 'refund_amount', 'reason']  # no approval_status here, it's set automatically
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        widgets = {
            'reason': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Enter reason for refund...'
            }),
            'refund_amount': forms.NumberInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Refund amount'
            }),
<<<<<<< HEAD
=======
        }


class AccountNoteForm(forms.ModelForm):
    class Meta:
        model = AccountNote
        fields = ('patient', 'invoice', 'note', 'is_pinned')
        widgets = {
            'patient': forms.Select(attrs={'class': 'w-full'}),
            'invoice': forms.Select(attrs={'class': 'w-full'}),
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a brief, helpful note…'}),
>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
        }