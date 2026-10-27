from django.db import transaction
from django.shortcuts import get_object_or_404, redirect,render
from django.views.generic import DetailView, ListView
from .models import Appointment, Doctor, Patient




class DoctorListView(ListView):
    model = Doctor
    template_name = 'doctor_list.html'
    context_object_name = 'doctors'


class DoctorDetailView(DetailView):
    template_name = 'doctor_detail.html'
    context_object_name = 'doctor'
    queryset = Doctor.objects.prefetch_related(
        'appointments__patient', 'appointments__diagnoses'
    )

    def get_object(self, queryset=None):
        doctor = super().get_object(queryset)
        doctor.total_appointments = len(doctor.appointments.all())
        return doctor

class DateFilterMixin:
    date_field = 'appt_date'
    doctor_field = 'doctor'

    def get_queryset(self):
        qs = super().get_queryset()
        date = self.request.GET.get('date', '')
        doctor = self.request.GET.get('doctor', '')
        if date:
            qs = qs.filter(**{self.date_field: date})
        if doctor:
            qs = qs.filter(**{self.doctor_field: doctor})
        return qs


class AppointmentListView(DateFilterMixin,ListView):
    template_name = 'appointment_list.html'
    context_object_name = 'appointments'
    queryset = Appointment.objects.select_related('doctor', 'patient')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.request.GET.get('date', '')
        context['doctors'] = Doctor.objects.all()
        doctor_id = self.request.GET.get('doctor', '')
        context['selected_doctor'] = int(doctor_id) if doctor_id.isdigit() else None
        context.setdefault('error', '')
        return context

    def post(self, request):
        error = ''
        doctor = get_object_or_404(Doctor, pk=request.POST.get('doctor'))
        policy = request.POST.get('policy', '').strip()
        appt_date = request.POST.get('appt_date')
        appt_time = request.POST.get('appt_time')

        input_name = request.POST.get('full_name', '').strip()

        with transaction.atomic():
            if Appointment.objects.filter(
                    doctor=doctor, appt_date=appt_date, appt_time=appt_time
            ).exists():
                error = 'Это время у врача уже занято'
            else:
                patient = Patient.objects.filter(policy=policy).first()

                if patient:
                    if patient.full_name.strip().lower() != input_name.lower():
                        error = 'Полис принадлежит другому пациенту, проверьте данные'
                    else:
                        Appointment.objects.create(
                            doctor=doctor,
                            patient=patient,
                            appt_date=appt_date,
                            appt_time=appt_time,
                        )
                        return redirect('clinic:appointment_list')
                else:
                    patient = Patient.objects.create(
                        policy=policy,
                        full_name=input_name,
                        birth_date=request.POST.get('birth_date'),
                        phone=request.POST.get('phone', '').strip(),
                    )
                    Appointment.objects.create(
                        doctor=doctor,
                        patient=patient,
                        appt_date=appt_date,
                        appt_time=appt_time,
                    )
                    return redirect('clinic:appointment_list')


        if error:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['error'] = error
            return self.render_to_response(context)



class PatientListView(ListView):
    template_name = 'patient_list.html'
    context_object_name = 'patients'
    queryset = Patient.objects.prefetch_related('appointments__diagnoses')