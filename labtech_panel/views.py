from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import LabTestRequest
from core.models import Patient
from django.utils.dateparse import parse_date
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import LabTestRequest
from core.models import Patient
from django.utils.dateparse import parse_date

from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
import weasyprint
from weasyprint import HTML
from django.contrib.auth.decorators import user_passes_test
<<<<<<< HEAD
=======
from doctor_panel.utils import get_comm_context
from doctor_panel.models import ReferralRequest


>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf


@login_required
def labtech_dashboard(request):
    # Upload Lab Result (POST)
    if request.method == 'POST':
        test_id = request.POST.get('test_request_id')
        result_text = request.POST.get('result')
        attachment = request.FILES.get('attachment')

        if test_id and result_text:
            try:
                lab_request = LabTestRequest.objects.get(id=test_id)
                lab_request.result = result_text
                lab_request.status = 'Completed'

                if attachment:
                    lab_request.attachment = attachment

                lab_request.save()
            except LabTestRequest.DoesNotExist:
                pass

    # Filtered list for display
    test_requests = LabTestRequest.objects.filter(status='Pending')
    patients = Patient.objects.all()
    test_types = LabTestRequest.objects.values_list('test_type', flat=True).distinct()
<<<<<<< HEAD
     # Summary stats
    total_tests = LabTestRequest.objects.count()
    completed_tests = LabTestRequest.objects.filter(status='Completed').count()
    pending_tests = LabTestRequest.objects.filter(status='Pending').count()

    completed_requests = LabTestRequest.objects.filter(status='Completed')


=======

    # Summary stats
    total_tests = LabTestRequest.objects.count()
    completed_tests = LabTestRequest.objects.filter(status='Completed').count()
    pending_tests = LabTestRequest.objects.filter(status='Pending').count()
    completed_requests = LabTestRequest.objects.filter(status='Completed')

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    patient_id = request.GET.get('patient')
    test_type = request.GET.get('type')
    date_str = request.GET.get('date')

    if patient_id:
        test_requests = test_requests.filter(patient__id=patient_id)

    if test_type:
        test_requests = test_requests.filter(test_type=test_type)

    if date_str:
        try:
            parsed_date = parse_date(date_str)
            if parsed_date:
                test_requests = test_requests.filter(requested_at=parsed_date)
        except ValueError:
            pass

    # ✅ Separate unfiltered pending requests list for dropdown
    pending_requests_all = LabTestRequest.objects.filter(status='Pending')

<<<<<<< HEAD
=======
    # ✅ Add referrals for dashboard display
    referrals = ReferralRequest.objects.all().order_by('-created_at')  # latest first

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    context = {
        'test_requests': test_requests,
        'pending_requests_all': pending_requests_all,
        'patients': patients,
        'test_types': test_types,
        'total_tests': total_tests,
        'completed_tests': completed_tests,
        'pending_tests': pending_tests,
        'completed_requests': completed_requests,
<<<<<<< HEAD
    }

=======
        'referrals': referrals,  # <-- new
    }

    context.update(get_comm_context(request.user, scope="all", limit=5))

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    return render(request, 'labtech_panel/dashboard.html', context)

def is_lab_tech(user):
    return user.groups.filter(name='LabTechnicians').exists()


def print_lab_report(request, pk):
    test = get_object_or_404(LabTestRequest, id=pk)

    html_string = render_to_string('labtech_panel/lab_report_template.html', {'test': test})
    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=lab_report_{pk}.pdf'
    return response

def download_lab_pdf(request, pk):
    report = get_object_or_404(LabTestRequest, pk=pk)
    html = render_to_string('labtech_panel/lab_report_template.html', {'test': report})  # changed
    pdf = weasyprint.HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="lab_report_{report.id}.pdf"'
    return response
