from django.urls import path
from .views import register, login, upload_wares, retrieve_wares

urlpatterns = [
    path('merchants/register', register, name='register'),
    path('merchants/login', login, name='login'),
    path('merchants/upload-wares', upload_wares, name='upload_wares'),
    path('wares', retrieve_wares, name='retrieve_wares'),
]