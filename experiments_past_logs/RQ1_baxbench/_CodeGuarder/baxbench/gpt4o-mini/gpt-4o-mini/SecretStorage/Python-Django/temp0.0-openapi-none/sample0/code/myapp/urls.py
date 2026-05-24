from django.urls import path
from .views import UserRegistrationView, UserLoginView, SetSecretView, GetSecretView

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
    path('set_secret', SetSecretView.as_view(), name='set_secret'),
    path('get_secret', GetSecretView.as_view(), name='get_secret'),
]