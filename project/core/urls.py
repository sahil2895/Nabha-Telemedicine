from django.urls import path
from . import views, api_views

urlpatterns = [
    # Page URLs
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("patient/dashboard/", views.patient_dashboard, name="patient_dashboard"),
    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("appointments/", views.AppointmentView.as_view(), name="appointments"),
    path("meeting/<int:appointment_id>/", views.start_meeting, name="start_meeting"),
    path("schedule/", views.manage_schedule, name="manage_schedule"),
    path("patient-records/", views.patient_records_view, name="patient_records"),
    
    # API endpoints
    path("api/health-records/", api_views.health_records_list, name="health_records_api"),
    path("api/appointments/<int:appointment_id>/status/", api_views.update_appointment_status, name="update_appointment_status"),
    path("api/symptoms/analyze/", api_views.analyze_symptoms, name="analyze_symptoms"),
    path("api/medicines/search/", api_views.search_medicines, name="search_medicines"),
    path("api/doctor/schedule/", api_views.get_doctor_schedule, name="get_doctor_schedule"),
    path("api/doctor/schedule/update/", api_views.update_doctor_schedule, name="update_doctor_schedule"),
    path("api/patients/list/", api_views.patient_list, name="patient_list"),
    path("api/patients/records/", api_views.get_patient_records, name="get_patient_records"),
    path("api/prescriptions/create/", api_views.create_prescription, name="create_prescription"),
    path("api/health-records/create/", api_views.create_health_record, name="create_health_record"),
    path("api/appointments/", api_views.get_appointments, name="get_appointments_api"),
]
