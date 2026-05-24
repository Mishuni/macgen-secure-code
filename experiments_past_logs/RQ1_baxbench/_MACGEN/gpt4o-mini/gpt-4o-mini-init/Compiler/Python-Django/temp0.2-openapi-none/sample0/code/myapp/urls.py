from django.urls import path
from .views import compile_code

urlpatterns = [
    path('compile', compile_code),
]