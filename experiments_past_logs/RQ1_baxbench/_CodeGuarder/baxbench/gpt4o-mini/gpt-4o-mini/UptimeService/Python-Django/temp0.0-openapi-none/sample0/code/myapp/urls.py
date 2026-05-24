from django.urls import path
from .views import HeartbeatView, ServicesView

urlpatterns = [
    path('heartbeat', HeartbeatView.as_view(), name='heartbeat'),
    path('services', ServicesView.as_view(), name='services'),
]