from django.urls import path
from .views import log_message

urlpatterns = [
    path('log', log_message),
    path('logs', log_message),
]