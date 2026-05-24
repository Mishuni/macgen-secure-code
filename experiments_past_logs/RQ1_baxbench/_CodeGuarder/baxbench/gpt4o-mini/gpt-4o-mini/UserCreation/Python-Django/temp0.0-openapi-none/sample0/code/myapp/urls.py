from django.urls import path
from .views import invite_user, create_user

urlpatterns = [
    path('invite_user', invite_user, name='invite_user'),
    path('create_user', create_user, name='create_user'),
]