from django.urls import path
from .views import search_files

urlpatterns = [
    path('', search_files),
]