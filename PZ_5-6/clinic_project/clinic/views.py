from django.shortcuts import render, get_object_or_404,redirect
from .models import Doctor, Appointment, Patient


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
    error = ''

    if request.method == 'POST':
        doctor = get_object_or_404(Doctor, pk=request.POST.get('doctor'))
        policy = request.POST.get('policy', '').strip()

        if Patient.objects.filter(policy=policy).exists():
            error = 'Пациент с таким полисом уже существует'
        else:
            patient = Patient.objects.create(
                full_name=request.POST.get('full_name'),
                birth_date=request.POST.get('birth_date'),
                policy=policy,
                phone=request.POST.get('phone'),
            )
            Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                appt_date=request.POST.get('appt_date'),
                appt_time=request.POST.get('appt_time'),
            )
            return redirect('appointment_list')

    date = request.GET.get('date', '')
    appointments = Appointment.objects.select_related('doctor', 'patient')

    if date:
        appointments = appointments.filter(appt_date=date)

    return render(request, 'appointment_list.html', {
        'appointments': appointments,
        'selected_date': date,
        'doctors': Doctor.objects.all(),
        'error': error,
    })

def patient_list(request):
    patients = Patient.objects.prefetch_related('appointments__diagnoses')
    return render(request, 'patient_list.html', {'patients': patients})