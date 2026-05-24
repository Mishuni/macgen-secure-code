from django.urls import path
from .views import convert_pdf

urlpatterns = [
    path('', convert_pdf, name='convert'),
]