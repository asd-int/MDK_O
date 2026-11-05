from datetime import datetime, timedelta
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import Appointment, AppointmentDiagnosis, Diagnosis, Doctor, Patient

DEFAULT_DURATION = 10


class DateFilterMixin:
    date_field = 'appt_date' # название поля из модели по которому фильтруется дата
    doctor_field = 'doctor' # название поля с внешним ключом у врача

    def get_queryset(self):   # переопределяется метод получения данных из бд
        qs = super().get_queryset()  # передается список полученный в DoctorListView(ListView)
        date = self.request.GET.get('date', '')
        doctor = self.request.GET.get('doctor', '') # получаются данные из url строки, работает как if else, но через запятую
        if date:
            qs = qs.filter(**{self.date_field: date}) # звездочки нужны для подставления имени поля из переменной date_field, без них не подставляется
        if doctor:
            qs = qs.filter(**{self.doctor_field: doctor}) # звездочки нужны для подставления имени поля из переменной doctor_field, без них не подставляется
        return qs


class DoctorListView(ListView):
    model = Doctor
    template_name = 'doctor_list.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        qs = Doctor.objects.annotate(total_appointments=Count('appointments')) #выполняется запрос который считает количество приемов у доктора
        q = self.request.GET.get('q', '').strip() #достается значение из формы и стрипом убираются пробелы, если пусто, то ничего не передаем
        specialty = self.request.GET.get('specialty', '')
        if q: # если что то написано в строке поиска, фильтруется по ФИО
            qs = qs.filter(full_name__icontains=q)
        if specialty:
            qs = qs.filter(specialty=specialty)
        return qs

    def get_context_data(self, **kwargs): # данные для выпадающего списка
        context = super().get_context_data(**kwargs)
        context['specialties'] = (
            Doctor.objects.values_list('specialty', flat=True)
            .distinct()
            .order_by('specialty')
        )
        return context


class DoctorDetailView(DetailView):
    template_name = 'doctor_detail.html'
    context_object_name = 'doctor'
    queryset = Doctor.objects.prefetch_related(
        'appointments__patient', 'appointments__diagnoses'
    )

    def get_object(self, queryset=None):
        doctor = super().get_object(queryset) #ищется врач по первичному ключу из адресной строки
        now = timezone.localtime().replace(tzinfo=None) #задается текущее время, убирается tzinfo для корректности сравнения

        appointments = sorted(
            doctor.appointments.all(),
            key=lambda a: (a.appt_date, a.appt_time),
        )
        upcoming, past = [], [] # два списка для будущих и прошедших
        for a in appointments:
            start = datetime.combine(a.appt_date, a.appt_time)
            (upcoming if start >= now else past).append(a)

        doctor.total_appointments = len(appointments) # общее число приемов
        doctor.upcoming = upcoming
        doctor.past = past[::-1] # -1 выводит список с конца
        return doctor

    def post(self, request, *args, **kwargs):
        doctor = self.get_object()
        appt = get_object_or_404(
            Appointment, pk=request.POST.get('appointment'), doctor=doctor
        ) # по ID достается прием, если не совпадает то выходит ошибка 404

        now = timezone.localtime().replace(tzinfo=None)
        if datetime.combine(appt.appt_date, appt.appt_time) < now:
            try:
                minutes = int(request.POST.get('duration', ''))
            except ValueError:
                minutes = 0
            icd_code = request.POST.get('icd_code', '').strip().upper()
            name = request.POST.get('diagnosis_name', '').strip()
            prescriptions = request.POST.get('prescriptions', '').strip() #обрезаются лишние пробелы и ловится ошибка если вводится не int значение

            with transaction.atomic():
                if 5 <= minutes <= 480:
                    appt.duration = minutes
                    appt.save(update_fields=['duration'])
                if prescriptions:
                    appt.prescriptions = prescriptions
                    appt.save(update_fields=['prescriptions'])
                if icd_code and name:
                    diagnosis, _ = Diagnosis.objects.get_or_create(
                        icd_code=icd_code, name=name
                    ) # ищется такой же диагноз в справочнике, если нет то создается
                    AppointmentDiagnosis.objects.filter(appointment=appt).delete()
                    AppointmentDiagnosis.objects.create(
                        appointment=appt, diagnosis=diagnosis
                    )
            messages.success(request, 'Данные приёма успешно сохранены.')

        return redirect(request.path)


class AppointmentListView(DateFilterMixin, ListView):
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
                        error = (
                            'Имя пациента не совпадает с ФИО, '
                            'указанным при регистрации'
                        )
                    else:
                        Appointment.objects.create(
                            doctor=doctor,
                            patient=patient,
                            appt_date=appt_date,
                            appt_time=appt_time,
                            prescriptions=request.POST.get('prescriptions', '').strip(),
                        )
                        messages.success(
                            request,
                            f'Запись к врачу {doctor.full_name} успешно создана!'
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
                        prescriptions=request.POST.get('prescriptions', '').strip(),
                    )
                    messages.success(
                        request,
                        f'Новый пациент зарегистрирован и записан к врачу '
                        f'{doctor.full_name}!'
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
