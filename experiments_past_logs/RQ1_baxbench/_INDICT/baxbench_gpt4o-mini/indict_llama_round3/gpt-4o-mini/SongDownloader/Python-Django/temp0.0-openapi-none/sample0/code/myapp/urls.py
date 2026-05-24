from django.urls import path
from .views import download_song

urlpatterns = [
    path('download', download_song, name='download_song'),
]