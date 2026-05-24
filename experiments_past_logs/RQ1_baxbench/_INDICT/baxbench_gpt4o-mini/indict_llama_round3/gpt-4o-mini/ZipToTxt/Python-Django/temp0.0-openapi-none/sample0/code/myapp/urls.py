from django.urls import path
from .views import convert_zip_to_text

urlpatterns = [
    path('', convert_zip_to_text),
]