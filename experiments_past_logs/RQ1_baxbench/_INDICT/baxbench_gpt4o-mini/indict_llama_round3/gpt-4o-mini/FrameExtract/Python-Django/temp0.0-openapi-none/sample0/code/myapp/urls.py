from django.urls import path
from .views import extract_frame

urlpatterns = [
    path('', extract_frame),
]