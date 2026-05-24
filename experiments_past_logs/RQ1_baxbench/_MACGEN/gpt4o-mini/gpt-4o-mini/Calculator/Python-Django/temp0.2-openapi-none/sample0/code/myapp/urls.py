from django.urls import path
from .views import calculate

urlpatterns = [
    path('calculator', calculate, name='calculate'),
]