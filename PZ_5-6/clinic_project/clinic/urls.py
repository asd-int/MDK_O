from django.urls import path
from . import views

app_name = 'clinic'

urlpatterns = [
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
]