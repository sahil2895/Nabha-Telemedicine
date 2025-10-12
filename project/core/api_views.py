from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import HealthRecord, Appointment, Doctor, Patient, Medicine, Pharmacy, PharmacyMedicine
from .serializers import (
    HealthRecordSerializer, AppointmentSerializer, DoctorSerializer,
    PatientSerializer, MedicineSerializer, PharmacySerializer
)
from django.db.models import Q
from datetime import datetime, timedelta

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def health_records_list(request):
    if not hasattr(request.user, 'patient'):
        return Response({'error': 'User is not a patient'}, status=status.HTTP_403_FORBIDDEN)
    
    records = HealthRecord.objects.filter(patient=request.user.patient)
    serializer = HealthRecordSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has permission to update this appointment
    if not request.user.is_doctor or request.user.doctor != appointment.doctor:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    new_status = request.data.get('status')
    if new_status not in [status for status, _ in Appointment.STATUS_CHOICES]:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    appointment.status = new_status
    appointment.save()
    return Response({'success': True, 'status': new_status})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_symptoms(request):
    symptoms = request.data.get('symptoms', '')
    if not symptoms:
        return Response({'error': 'No symptoms provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Simple symptom analysis (in a real system, this would use a more sophisticated AI model)
    common_conditions = {
        'fever': ['Common cold', 'Flu', 'COVID-19'],
        'headache': ['Migraine', 'Tension headache', 'Sinus infection'],
        'cough': ['Common cold', 'Bronchitis', 'Asthma'],
        'fatigue': ['Anemia', 'Depression', 'Sleep disorder'],
        'nausea': ['Food poisoning', 'Migraine', 'Stomach virus']
    }
    
    found_conditions = set()
    severity = 'low'
    
    for keyword, conditions in common_conditions.items():
        if keyword.lower() in symptoms.lower():
            found_conditions.update(conditions)
            
    if len(found_conditions) > 2:
        severity = 'moderate'
    if 'severe' in symptoms.lower() or 'intense' in symptoms.lower():
        severity = 'high'
        
    response = {
        'possible_conditions': list(found_conditions),
        'severity': severity,
        'recommendation': 'Please consult with a doctor for accurate diagnosis.' if severity != 'low' 
                         else 'Monitor your symptoms and rest. Consult a doctor if symptoms worsen.'
    }
    
    return Response(response)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_medicines(request):
    query = request.GET.get('query', '')
    if not query:
        return Response({'error': 'No search query provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    medicines = Medicine.objects.filter(
        Q(name__icontains=query) | Q(manufacturer__icontains=query)
    ).select_related()
    
    results = []
    for medicine in medicines:
        pharmacy_stocks = PharmacyMedicine.objects.filter(medicine=medicine, stock__gt=0)
        available_at = [
            {
                'pharmacy_name': pm.pharmacy.name,
                'pharmacy_address': pm.pharmacy.address,
                'stock': pm.stock,
                'price': float(medicine.price)
            }
            for pm in pharmacy_stocks
        ]
        
        results.append({
            'id': medicine.id,
            'name': medicine.name,
            'manufacturer': medicine.manufacturer,
            'description': medicine.description,
            'available_at': available_at
        })
    
    return Response(results)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_doctor_schedule(request):
    if not request.user.is_doctor:
        return Response({'error': 'User is not a doctor'}, status=status.HTTP_403_FORBIDDEN)
    
    doctor = request.user.doctor
    return Response({
        'available_times': doctor.available_times
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_doctor_schedule(request):
    if not request.user.is_doctor:
        return Response({'error': 'User is not a doctor'}, status=status.HTTP_403_FORBIDDEN)
    
    available_times = request.data.get('available_times', {})
    if not isinstance(available_times, dict):
        return Response({'error': 'Invalid schedule format'}, status=status.HTTP_400_BAD_REQUEST)
    
    doctor = request.user.doctor
    doctor.available_times = available_times
    doctor.save()
    
    return Response({'success': True, 'available_times': available_times})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_list(request):
    if not request.user.is_doctor:
        return Response({'error': 'User is not a doctor'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get all patients who have had appointments with this doctor
    patients = Patient.objects.filter(
        appointment__doctor=request.user.doctor
    ).distinct()
    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_patient_records(request):
    if not request.user.is_doctor:
        return Response({'error': 'User is not a doctor'}, status=status.HTTP_403_FORBIDDEN)
    
    patient_id = request.GET.get('patient_id')
    if not patient_id:
        # Return list of patients with basic info
        patients = Patient.objects.filter(
            appointment__doctor=request.user.doctor
        ).distinct()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)
    
    # Return detailed patient records
    patient = get_object_or_404(Patient, id=patient_id)
    records = HealthRecord.objects.filter(patient=patient)
    appointments = Appointment.objects.filter(
        doctor=request.user.doctor,
        patient=patient
    ).order_by('-date', '-time')
    
    return Response({
        'patient': PatientSerializer(patient).data,
        'health_records': HealthRecordSerializer(records, many=True).data,
        'appointments': AppointmentSerializer(appointments, many=True).data
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_prescription(request):
    if not request.user.is_doctor:
        return Response({'error': 'User is not a doctor'}, status=status.HTTP_403_FORBIDDEN)
    
    appointment_id = request.data.get('appointment_id')
    prescription_text = request.data.get('prescription')
    diagnosis = request.data.get('diagnosis')
    
    if not all([appointment_id, prescription_text]):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.doctor != request.user.doctor:
        return Response({'error': 'Not authorized to update this appointment'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    appointment.prescription = prescription_text
    if diagnosis:
        appointment.diagnosis = diagnosis
    appointment.status = 'completed'
    appointment.save()
    
    return Response({
        'success': True,
        'appointment': AppointmentSerializer(appointment).data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_appointments(request):
    if hasattr(request.user, 'doctor'):
        appointments = Appointment.objects.filter(doctor=request.user.doctor)
    elif hasattr(request.user, 'patient'):
        appointments = Appointment.objects.filter(patient=request.user.patient)
    else:
        return Response({'error': 'User is neither a doctor nor a patient'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_health_record(request):
    if not hasattr(request.user, 'patient'):
        return Response({'error': 'User is not a patient'}, status=status.HTTP_403_FORBIDDEN)
    
    record_type = request.data.get('record_type')
    description = request.data.get('description')
    file = request.FILES.get('file')
    date = request.data.get('date', datetime.now().date().isoformat())
    
    if not all([record_type, description]):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
    
    record = HealthRecord.objects.create(
        patient=request.user.patient,
        record_type=record_type,
        description=description,
        file=file,
        date=date
    )
    
    serializer = HealthRecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
