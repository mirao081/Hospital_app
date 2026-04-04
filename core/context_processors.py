from .models import HeaderSettings
from .models import Specialty
from .models import FooterSettings
from .forms import AppointmentForm
from .models import Message,Enquiry


def header_settings(request):
    try:
        settings = HeaderSettings.objects.first()
    except HeaderSettings.DoesNotExist:
        settings = None
    return {'header_settings': settings}

def trending_specialties(request):
    specialties = Specialty.objects.all()
    return {'specialties': specialties}



def footer_settings(request):
    footer = FooterSettings.objects.first()
    return {'footer_settings': footer}

def appointment_form_processor(request):
    return {
        'footer_appointment_form': AppointmentForm()
    }

def unread_message_context(request):
    context = {}

    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, is_read=False)
        context['unread_count'] = unread_messages.count()
        context['unread_messages'] = unread_messages[:5]
    else:
        context['unread_count'] = 0

    unread_enquiries = Enquiry.objects.filter(is_read=False)
    context['unread_enquiry_count'] = unread_enquiries.count()
    context['unread_enquiries'] = unread_enquiries[:5]

    # Total
    context['total_unread_count'] = context['unread_count'] + context['unread_enquiry_count']
    return context

def footer_form(request):
    return {
        'footer_appointment_form': AppointmentForm()
    }
