from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from .models import *
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count

DEFAULT_DURATION = 10

class DoctorListView(ListView):
    model = Doctor
    template_name = 'doctor_list.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        qs = Doctor.objects.annotate(total_appointments=Count('appointments'))
        q = self.request.GET.get('q', '').strip()
        specialty = self.request.GET.get('specialty', '')
        if q:
            qs = qs.filter(full_name__icontains=q)
        if specialty:
            qs = qs.filter(specialty=specialty)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialties'] = Doctor.objects.values_list('specialty', flat=True).distinct().order_by('specialty')
        return context


class DoctorDetailView(DetailView):
    template_name = 'doctor_detail.html'
    context_object_name = 'doctor'
    queryset = Doctor.objects.prefetch_related(
        'appointments__patient', 'appointments__diagnoses'
    )

    def get_object(self, queryset=None):
        doctor = super().get_object(queryset)
        now = timezone.localtime().replace(tzinfo=None)

        appointments = sorted(
            doctor.appointments.all(),
            key=lambda a: (a.appt_date, a.appt_time),
        )
        upcoming, past = [], []
        for a in appointments:
            start = datetime.combine(a.appt_date, a.appt_time)
            (upcoming if start >= now else past).append(a)

        doctor.total_appointments = len(appointments)
        doctor.upcoming = upcoming
        doctor.past = past[::-1]
        return doctor

    def post(self, request, *args, **kwargs):
        doctor = self.get_object()
        appt = get_object_or_404(
            Appointment, pk=request.POST.get('appointment'), doctor=doctor
        )

        now = timezone.localtime().replace(tzinfo=None)
        if datetime.combine(appt.appt_date, appt.appt_time) < now:
            try:
                minutes = int(request.POST.get('duration', ''))
            except ValueError:
                minutes = 0
            icd_code = request.POST.get('icd_code', '').strip().upper()
            name = request.POST.get('diagnosis_name', '').strip()

            with transaction.atomic():
                if 5 <= minutes <= 480:
                    appt.duration = minutes
                    appt.save(update_fields=['duration'])
                if icd_code and name:
                    # 1. диагноз в справочнике: берём существующий или создаём новый
                    diagnosis, _ = Diagnosis.objects.get_or_create(icd_code=icd_code, name=name)
                    # 2. связь с приёмом: прежнюю удаляем, новую создаём (перезапись)
                    AppointmentDiagnosis.objects.filter(appointment=appt).delete()
                    AppointmentDiagnosis.objects.create(appointment=appt, diagnosis=diagnosis)

        return redirect(request.path)


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
            start = datetime.fromisoformat(f'{appt_date} {appt_time}')
            end = start + timedelta(minutes=DEFAULT_DURATION)

            busy = False
            for a in Appointment.objects.filter(doctor=doctor, appt_date=appt_date):
                a_start = datetime.combine(a.appt_date, a.appt_time)
                if a_start < end and start < a_start + timedelta(minutes=a.duration):
                    busy = True
                    break

            if busy:
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

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['error'] = error
        return self.render_to_response(context)


class PatientListView(ListView):
    template_name = 'patient_list.html'
    context_object_name = 'patients'
    queryset = Patient.objects.prefetch_related('appointments__diagnoses').annotate(
        diag_count=Count('appointments__diagnoses')
    )