from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Doctor, Patient, Appointment, HealthRecord
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse

def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        
        if user_type == 'doctor':
            user.is_doctor = True
            user.is_patient = False
            user.save()
            doctor = Doctor.objects.create(
                user=user,
                specialization=request.POST.get('specialization', ''),
                license_number=request.POST.get('license_number', ''),
            )
        else:
            patient = Patient.objects.create(user=user)

        login(request, user)
        return redirect('home')

    return render(request, 'register.html')

@login_required
def patient_dashboard(request):
    if not request.user.is_patient:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient)
    context = {
        'appointments': appointments,
    }
    return render(request, 'patient_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    doctor = request.user.doctor
    appointments = Appointment.objects.filter(doctor=doctor)
    context = {
        'appointments': appointments,
    }
    return render(request, 'doctor_dashboard.html', context)

@method_decorator(login_required, name='dispatch')
class AppointmentView(View):
    def get(self, request):
        if request.user.is_patient:
            appointments = Appointment.objects.filter(patient=request.user.patient)
            doctors = Doctor.objects.all()
            return render(request, 'appointments.html', {
                'appointments': appointments,
                'doctors': doctors
            })
        else:
            appointments = Appointment.objects.filter(doctor=request.user.doctor)
            return render(request, 'appointments.html', {'appointments': appointments})

    def post(self, request):
        if not request.user.is_patient:
            return JsonResponse({'error': 'Only patients can book appointments'}, status=403)
        
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        time = request.POST.get('time')
        symptoms = request.POST.get('symptoms', '')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=request.user.patient,
                date=date,
                time=time,
                symptoms=symptoms
            )
            return JsonResponse({'message': 'Appointment booked successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required
def start_meeting(request, appointment_id):
    if not request.user.is_doctor:
        messages.error(request, 'Only doctors can start meetings')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)
    return render(request, 'meeting.html', {'appointment': appointment})

@login_required
def manage_schedule(request):
    if not request.user.is_doctor:
        messages.error(request, 'Only doctors can manage schedules')
        return redirect('home')
    
    context = {
        'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    }
    return render(request, 'schedule.html', context)

@login_required
def patient_records_view(request):
    if not request.user.is_doctor:
        messages.error(request, 'Only doctors can access patient records')
        return redirect('home')
    
    return render(request, 'patient_records.html')
