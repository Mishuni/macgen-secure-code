from django.urls import path
from .views import register_click, retrieve_clicks

urlpatterns = [
    path('click', register_click, name='register_click'),
    path('clicks', retrieve_clicks, name='retrieve_clicks'),
]