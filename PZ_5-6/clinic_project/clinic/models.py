from django.db import models

class Diagnosis (models.Model):
    icd_code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)

class Doctor (models.Model):
    full_name = models.CharField(max_length=150)
    specialty = models.CharField(max_length=100)
    cabinet = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)

class Patient(models.Model):
    full_name = models.CharField(max_length=150)
    birth_date = models.DateField()
    policy = models.CharField(max_length=20,unique=True)
    phone = models.CharField(max_length=20)

class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.RESTRICT, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.RESTRICT, related_name='appointments')
    appt_date = models.DateField()
    appt_time = models.TimeField()
    prescriptions = models.TextField()
    diagnoses = models.ManyToManyField(Diagnosis,through='AppointmentDiagnosis')
    duration = models.PositiveSmallIntegerField('Длительность, мин', default=30)


class AppointmentDiagnosis(models.Model):
    appointment = models.ForeignKey('Appointment',on_delete=models.CASCADE)
    diagnosis = models.ForeignKey('Diagnosis',on_delete=models.RESTRICT)