from django.urls import path
from .views import click_handler

urlpatterns = [
    path('click', click_handler, name='register_click'),
    path('clicks', click_handler, name='retrieve_clicks'),
]