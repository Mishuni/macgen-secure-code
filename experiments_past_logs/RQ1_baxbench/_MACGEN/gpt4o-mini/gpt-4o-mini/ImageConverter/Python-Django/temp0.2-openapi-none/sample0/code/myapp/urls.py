from django.urls import path
from .views import create_gif

urlpatterns = [
    path('create-gif', create_gif, name='create_gif'),
]