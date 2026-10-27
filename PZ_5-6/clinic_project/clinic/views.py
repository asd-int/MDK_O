from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
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

    def get_queryset(self):
        qs = super().get_queryset()
        date = self.request.GET.get('date', '')
        if date:
            qs = qs.filter(**{self.date_field: date})
        return qs


class AppointmentListView(DateFilterMixin,ListView):
    template_name = 'appointment_list.html'
    context_object_name = 'appointments'
    queryset = Appointment.objects.select_related('doctor', 'patient')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.request.GET.get('date', '')
        context['doctors'] = Doctor.objects.all()
        context.setdefault('error', '')
        return context

    def post(self, request, *args, **kwargs):
        error = ''
        doctor = get_object_or_404(Doctor, pk=request.POST.get('doctor'))
        policy = request.POST.get('policy', '').strip()
        appt_date = request.POST.get('appt_date')
        appt_time = request.POST.get('appt_time')

        with transaction.atomic():
            if Appointment.objects.filter(
                doctor=doctor, appt_date=appt_date, appt_time=appt_time
            ).exists():
                error = 'Это время у врача уже занято'
            else:
                patient, created = Patient.objects.get_or_create(
                    policy=policy,
                    defaults={
                        'full_name': request.POST.get('full_name'),
                        'birth_date': request.POST.get('birth_date'),
                        'phone': request.POST.get('phone'),
                    },
                )
                Appointment.objects.create(
                    doctor=doctor,
                    patient=patient,
                    appt_date=appt_date,
                    appt_time=appt_time,
                )
                return redirect('clinic:appointment_list')

        # при ошибке заново отрисовываем страницу со списком и сообщением
        self.object_list = self.get_queryset()
        context = self.get_context_data(error=error)
        return self.render_to_response(context)


class PatientListView(ListView):
    template_name = 'patient_list.html'
    context_object_name = 'patients'
    queryset = Patient.objects.prefetch_related('appointments__diagnoses')