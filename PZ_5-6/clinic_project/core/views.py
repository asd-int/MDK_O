from datetime import datetime
from django.shortcuts import render
from django.utils import timezone
from clinic.models import Doctor, Patient, Appointment


def home(request):
    now = timezone.localtime().replace(tzinfo=None)

    future = (
        Appointment.objects
        .filter(appt_date__gte=now.date())
        .select_related('doctor', 'patient')
        .order_by('appt_date', 'appt_time')
    )
    upcoming = [
        a for a in future
        if datetime.combine(a.appt_date, a.appt_time) >= now
    ][:5]

    return render(request, 'home.html', {
        'doctors_count': Doctor.objects.count(),
        'patients_count': Patient.objects.count(),
        'appointments_count': Appointment.objects.count(),
        'upcoming_appointments': upcoming,
    })