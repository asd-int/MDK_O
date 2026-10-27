from django.urls import path
from . import views

app_name = "clinic"

urlpatterns = [
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('patients/', views.patient_list, name='patient_list'),
]