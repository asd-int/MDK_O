from django.shortcuts import render
from clinic.models import Doctor, Patient, Appointment


def home(request):
    context = {
        'doctors_count': Doctor.objects.count(),
        'patients_count': Patient.objects.count(),
        'appointments_count': Appointment.objects.count(),
    }
    return render(request, 'core/home.html', context)