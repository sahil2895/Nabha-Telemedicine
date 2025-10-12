from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Doctor, Patient, Appointment, HealthRecord, Medicine, Pharmacy, PharmacyMedicine

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_doctor', 'is_patient', 'is_staff')
    list_filter = ('is_doctor', 'is_patient', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_doctor', 'is_patient', 'phone_number', 'address')}),
    )

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number', 'experience_years')
    search_fields = ('user__username', 'specialization', 'license_number')

class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'blood_group')
    search_fields = ('user__username', 'blood_group')

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('doctor__user__username', 'patient__user__username')

class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'record_type', 'is_private')
    list_filter = ('record_type', 'is_private')
    search_fields = ('patient__user__username', 'record_type')

class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'is_available', 'price', 'stock')
    list_filter = ('is_available', 'manufacturer')
    search_fields = ('name', 'manufacturer')

class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email')
    search_fields = ('name', 'email')

class PharmacyMedicineAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'medicine', 'stock', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('pharmacy__name', 'medicine__name')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(HealthRecord, HealthRecordAdmin)
admin.site.register(Medicine, MedicineAdmin)
admin.site.register(Pharmacy, PharmacyAdmin)
admin.site.register(PharmacyMedicine, PharmacyMedicineAdmin)
