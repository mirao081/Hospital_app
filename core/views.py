from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django import forms
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from core.models import Message 
from core.models import Patient



from .forms import AppointmentForm, EnquiryForm,AssignBedForm
from .models import (
    AboutSection, FeaturedDoctor, HighlightItem, InfoCard, UserReview,
    Article, DoctorCTA, HeaderSettings, FooterSettings, Doctor,
    DoctorsPageSettings, Blog, FeaturedBlog, Department, Testimonial, ContactInfo,
    Specialty, Appointment, ActivityLog,Bed  # Ensure ActivityLog is imported
    
)

User = get_user_model()

# ========================
# CONSTANTS
# ========================

ROLES = ['admin', 'doctor', 'labtech', 'nurse', 'receptionist', 'pharmacist', 'patient','cashier',]

# ========================
# AUTH VIEWS
# ========================

@csrf_protect
def custom_login_view(request):
    context = {'roles': ROLES}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            user_role = getattr(user, 'role', None)

            if user_role != selected_role:
                context['error'] = 'Incorrect role selected for this user.'
                return render(request, 'core/login.html', context)

            login(request, user)

            ActivityLog.objects.create(
                user=user,
                action='LOGIN',
                description='User logged in.'
            )

            return redirect('role_redirect')
        else:
            context['error'] = 'Invalid username or password.'

    return render(request, 'core/login.html', context)


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            ActivityLog.objects.create(
                user=user,
                action='REGISTER',
                description='New patient account registered.'
            )

            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})


def logout_view(request):
    ActivityLog.objects.create(
        user=request.user,
        action='LOGOUT',
        description='User logged out.'
    )
    logout(request)
    return redirect('landing_page')


# ========================
# LANDING & HOME
# ========================

def landing_page(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_panel:admin_dashboard')

    appointment_form = AppointmentForm()
    if appointment_form.is_valid():
        appointment_form.save()
        messages.success(request, "Appointment booked successfully.")
        return redirect('landing_page')

    login_form = AuthenticationForm(request, data=request.POST if request.POST.get('form_type') == 'login' else None)
    if login_form.is_valid():
        user = login_form.get_user()
        login(request, user)
        return redirect('role_redirect')

    reviews = UserReview.objects.all().order_by('-id')[:5]
    for review in reviews:
        review.remaining_stars = 5 - review.rating

    context = {
        'form': appointment_form,
        'login_form': login_form,
        'specialties': Specialty.objects.all(),
        'about': AboutSection.objects.first(),
        'doctors': Doctor.objects.filter(is_featured=True)[:6],
        'highlights': HighlightItem.objects.all()[:4],
        'info_cards': InfoCard.objects.all(),
        'reviews': reviews,
        'latest_articles': Article.objects.order_by('-date_published')[:10],
        'doctor_cta': DoctorCTA.objects.first(),
        'header_settings': HeaderSettings.objects.first(),
        'footer_settings': FooterSettings.objects.first(),
        'footer_appointment_form': appointment_form,

        # ✅ ADD THIS LINE:
        'range_1_to_5': range(1, 6),
    }

    return render(request, 'core/landing.html', context)


# ========================
# BLOGS & DOCTORS
# ========================

def blogs_view(request):
    blogs = Blog.objects.all().order_by('-created_at')
    form = AppointmentForm()
    footer_settings = FooterSettings.objects.first()  # ✅ Fetch footer config

    settings = {
        "title": "Blog",
        "breadcrumb_home_text": "Home",
        "breadcrumb_text": "Blog",
        "background_color": "aliceblue",
    }

    return render(request, 'core/blogs.html', {
        'blogs': blogs,
        'settings': settings,
        'form': form,
        'footer_settings': footer_settings,  # ✅ Pass to template
    })

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'core/blog_detail.html', {'blog': blog})


def blog_highlight_section(request):
    blogs = FeaturedBlog.objects.all()[:3]
    settings = {
        "title": "Blog",
        "breadcrumb_home_text": "Home",
        "breadcrumb_text": "Blog"
    }
    return render(request, 'core/blog_highlight.html', {'blogs': blogs, 'settings': settings})


def doctors_list(request):
    doctors = Doctor.objects.filter(is_featured=True)
    form = AppointmentForm()
    settings = {
        "title": "Doctors",
        "breadcrumb_home_text": "Home",
        "height": "100vh",
        "background_color": "aliceblue"
    }
    return render(request, 'core/doctors_list.html', {
        'doctors': doctors,
        'settings': settings,
        'form': form,
    })


def doctors_page(request):
    settings = DoctorsPageSettings.objects.first()
    doctors = Doctor.objects.all()
    form = AppointmentForm()
    return render(request, 'core/doctors.html', {
        'settings': settings,
        'doctors': doctors,
        'form': form,
    })


def departments_view(request):
    departments = Department.objects.all().prefetch_related('doctors')
    settings = {
        "title": "Departments",
        "breadcrumb_home_text": "Home",
        "breadcrumb_text": "Departments",
        "background_color": "aliceblue",
    }
    return render(request, 'core/departments.html', {
        'departments': departments,
        'settings': settings
    })


def doctors_by_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    doctors = Doctor.objects.filter(department=department)
    return render(request, 'core/doctors_by_department.html', {
        'department': department,
        'doctors': doctors
    })


# ========================
# CONTACT & MISC PAGES
# ========================

# core/views.py
def contact_view(request):
    contact = ContactInfo.objects.first()
    form = EnquiryForm()

    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            print("✅ Enquiry saved:", enquiry)  # Add this to verify

            # Skip email for now to avoid TimeoutError
            messages.success(request, "Your message has been saved!")

            return redirect('contact')
        else:
            print("❌ Form errors:", form.errors)

    return render(request, 'core/contact.html', {'form': form, 'contact': contact})


def terms_view(request):
    return render(request, 'core/terms.html')


def privacy_policy_view(request):
    return render(request, 'core/privacy.html')


def refund_policy(request):
    return render(request, 'core/refund.html')


def testimonials_view(request):
    testimonials = Testimonial.objects.all()
    return render(request, 'core/testimonials.html', {'testimonials': testimonials})


# ========================
# APPOINTMENTS
# ========================

@require_POST
def footer_appointment(request):
    form = AppointmentForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'You have successfully booked an appointment.')
    else:
        messages.error(request, 'There was an error in your form. Please check and try again.')
        print("❌ Appointment form errors:", form.errors)
    
    # Redirect back to the same page (safe fallback)
    return redirect(request.META.get('HTTP_REFERER', '/'))

def appointment_view(request):
    if request.method == 'POST':
        print("📨 Received POST request:", request.POST)
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)

            # ✅ Set patient if user is logged in and is a patient
            if request.user.is_authenticated:
                try:
                    patient = Patient.objects.get(user=request.user)
                    appointment.patient = patient
                except Patient.DoesNotExist:
                    print("⚠️ Logged-in user is not a registered patient.")

            appointment.save()
            print("✅ Appointment saved:", appointment)

            # ✉️ 1. Message to the doctor
            try:
                doctor_user = appointment.doctor.user
                Message.objects.create(
                    sender=request.user if request.user.is_authenticated else None,
                    recipient=doctor_user,
                    subject="New Appointment",
                    body=f"You have a new appointment with {appointment.full_name} on {appointment.date} at {appointment.time}.",
                )
                print("📨 Doctor notified.")
            except Exception as e:
                print("⚠️ Could not send message to doctor:", e)

            # ✉️ 2. Message to all admins
            try:
                admin_users = User.objects.filter(is_staff=True)
                for admin_user in admin_users:
                    Message.objects.create(
                        sender=request.user if request.user.is_authenticated else None,
                        recipient=admin_user,
                        subject="New Appointment Submitted",
                        body=f"New appointment for Dr. {appointment.doctor.user.get_full_name()} by {appointment.full_name}.",
                    )
                print("📨 All admins notified.")
            except Exception as e:
                print("⚠️ Could not send messages to admins:", e)

            return redirect('success_page')
        else:
            print("❌ Form errors:", form.errors)
    else:
        form = AppointmentForm()

    return render(request, 'core/appointment.html', {'form': form})


@login_required
def role_based_redirect_view(request):
    role_to_dashboard = {
        'admin': 'admin_panel:admin_dashboard',
        'doctor': 'doctor:doctor_dashboard',
        'nurse': 'nurse:nurse_dashboard',
        'receptionist': 'receptionist:receptionist_dashboard',
        'pharmacist': 'pharmacist_panel:dashboard',
        'labtech': 'labtech_panel:labtech_dashboard',
        'patient': 'patient:patient_dashboard',
        'cashier': 'cashier:cashier_dashboard',  # ✅ Fixed here
    }
    return redirect(role_to_dashboard.get(request.user.role, 'landing_page'))


# Optional placeholder for success redirect if missing
def success_page(request):
    return render(request, 'core/success.html')


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def assign_bed_view(request):
    if request.method == 'POST':
        form = AssignBedForm(request.POST)

        # Update bed queryset dynamically
        room_id = request.POST.get('room')
        if room_id:
            form.fields['bed'].queryset = Bed.objects.filter(room_id=room_id, is_occupied=False, patient__isnull=True)

        if form.is_valid():
            bed = form.cleaned_data['bed']
            patient = form.cleaned_data['patient']

            bed.patient = patient
            bed.is_occupied = True
            bed.save()

            messages.success(request, f"{patient.user.get_full_name()} assigned to {bed}")
            return redirect('assign_bed')
    else:
        form = AssignBedForm()

    return render(request, 'core/assign_bed.html', {'form': form})

# to unassign bed 
@login_required
@user_passes_test(is_admin)
def unassign_bed_view(request, bed_id):
    bed = get_object_or_404(Bed, id=bed_id)

    if request.method == 'POST':
        bed.patient = None
        bed.is_occupied = False
        bed.save()
        messages.success(request, f"{bed} has been unassigned.")
        return redirect('assign_bed')

    return render(request, 'core/unassign_bed_confirm.html', {'bed': bed})
