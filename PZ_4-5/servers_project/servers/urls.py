from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('history/', views.history_view, name='history'),
]