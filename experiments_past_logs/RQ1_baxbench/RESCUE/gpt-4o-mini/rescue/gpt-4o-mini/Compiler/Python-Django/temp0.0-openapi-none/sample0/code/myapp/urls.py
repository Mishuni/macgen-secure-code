from django.urls import path
from .views import compile_code

urlpatterns = [
    path('', compile_code, name='compile_code'),
]