from django import template
from django.db.models import Count

from clinic.models import Appointment, Doctor

register = template.Library()


# 1. Simple Tag: общее количество записей на приём
@register.simple_tag
def total_appointments():
    """Возвращает общее количество записей на приём."""
    return Appointment.objects.count()


# 2. Inclusion Tag: самые загруженные врачи
@register.inclusion_tag('clinic/tags/busy_doctors.html')
def show_busy_doctors(count=3):
    """Отображает врачей с наибольшим числом записей."""
    doctors = Doctor.objects.annotate(
        appointments_count=Count('appointments')
    ).order_by('-appointments_count')[:count]
    return {'doctors': doctors}


# 3. Custom Filter: длительность в минутах -> «1 ч 30 мин»
@register.filter
def duration_minutes(value):
    """Преобразует число минут в читаемую длительность."""
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