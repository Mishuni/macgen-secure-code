from django.urls import path
from .views import monitor_processes

urlpatterns = [
    path('commands', monitor_processes),
]