from django.urls import path
from .views import register_heartbeat, get_services

urlpatterns = [
    path('heartbeat', register_heartbeat, name='register_heartbeat'),
    path('services', get_services, name='get_services'),
]