from django.shortcuts import render, get_object_or_404
from .models import Doctor, Appointment

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctor_list.html', {'doctors': doctors})

def doctor_detail(request, pk):
    doctor = get_object_or_404(
        Doctor.objects.prefetch_related('appointments__patient', 'appointments__diagnoses'),
        pk=pk
    )
    return render(request, 'doctor_detail.html', {'doctor': doctor})

def appointment_list(request):
    date = request.GET.get('date', '')
    appointments = Appointment.objects.select_related(
        'doctor', 'patient'
    ).prefetch_related('diagnoses')

    if date:
        appointments = appointments.filter(appt_date=date)

    return render(request, 'appointment_list.html', {
        'appointments': appointments,
        'selected_date': date,
    })

