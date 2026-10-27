from django import template
from django.db.models import Count

from clinic.models import Appointment, Doctor

register = template.Library()



@register.simple_tag
def total_appointments():
    return Appointment.objects.count()



@register.inclusion_tag('clinic/tags/busy_doctors.html')
def show_busy_doctors(count=3):

    doctors = Doctor.objects.annotate(
        appointments_count=Count('appointments')
    ).order_by('-appointments_count')[:count]
    return {'doctors': doctors}



@register.filter
def duration_minutes(value):
    try:
        minutes = int(value)
    except (ValueError, TypeError):
        return value
    if minutes <= 0:
        return '0 мин'
    hours, mins = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f'{hours} ч')
    if mins:
        parts.append(f'{mins} мин')
    return ' '.join(parts)