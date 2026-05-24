from django.urls import path
from .views import MonitorView

urlpatterns = [
    path('commands', MonitorView.as_view(), name='monitor_commands'),
]