from rest_framework import serializers
from .models import HealthRecord, Appointment, Doctor, Patient, Medicine, Pharmacy

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialization', 'experience_years', 'available_times']

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Patient
        fields = ['id', 'user', 'date_of_birth', 'blood_group', 'emergency_contact']

class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = ['id', 'date', 'record_type', 'file', 'description', 'is_private']

class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'patient', 'date', 'time', 'status', 'symptoms', 'diagnosis', 'prescription', 'meeting_link']

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'manufacturer', 'description', 'is_available', 'price', 'stock']

class PharmacySerializer(serializers.ModelSerializer):
    medicines = MedicineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pharmacy
        fields = ['id', 'name', 'address', 'phone_number', 'email', 'medicines']
