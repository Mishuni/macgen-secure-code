from django.urls import path
from .views import upload_image, share_image

urlpatterns = [
    path('upload', upload_image, name='upload_image'),
    path('images/<int:imageId>', share_image, name='share_image'),
]