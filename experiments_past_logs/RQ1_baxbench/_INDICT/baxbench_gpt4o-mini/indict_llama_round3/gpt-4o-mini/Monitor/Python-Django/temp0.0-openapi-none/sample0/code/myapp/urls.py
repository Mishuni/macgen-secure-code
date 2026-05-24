from django.urls import path
from .views import MonitorProcesses

urlpatterns = [
    path('commands', MonitorProcesses.as_view(), name='monitor_processes'),
]