from django.urls import path
from .views import RegisterView, LoginView, SetSecretView, GetSecretView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('set_secret', SetSecretView.as_view(), name='set_secret'),
    path('get_secret', GetSecretView.as_view(), name='get_secret'),
]