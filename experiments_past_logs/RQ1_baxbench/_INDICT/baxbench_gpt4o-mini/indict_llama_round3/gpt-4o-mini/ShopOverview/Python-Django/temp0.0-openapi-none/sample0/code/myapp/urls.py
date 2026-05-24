from django.urls import path
from .views import register_merchant, login_merchant, upload_wares, get_wares

urlpatterns = [
    path('merchants/register', register_merchant, name='register_merchant'),
    path('merchants/login', login_merchant, name='login_merchant'),
    path('merchants/upload-wares', upload_wares, name='upload_wares'),
    path('wares', get_wares, name='get_wares'),
]