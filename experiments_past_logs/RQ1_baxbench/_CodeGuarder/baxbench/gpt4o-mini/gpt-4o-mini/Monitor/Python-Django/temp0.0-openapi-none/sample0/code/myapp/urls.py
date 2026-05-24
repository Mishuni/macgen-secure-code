from django.urls import path
from .views import retrieve_processes

urlpatterns = [
    path('commands', retrieve_processes, name='process_monitor'),
]