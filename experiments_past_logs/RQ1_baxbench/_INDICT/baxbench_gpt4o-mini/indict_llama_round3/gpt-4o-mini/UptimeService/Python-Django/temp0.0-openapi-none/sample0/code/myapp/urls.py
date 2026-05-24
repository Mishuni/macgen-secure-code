from django.urls import path
from .views import heartbeat, services

urlpatterns = [
    path('heartbeat', heartbeat, name='heartbeat'),
    path('services', services, name='services'),
]