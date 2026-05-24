from django.urls import path
from .views import ImageUploadView, ImageRetrieveView

urlpatterns = [
    path('upload', ImageUploadView.as_view(), name='image-upload'),
    path('images/<str:imageId>', ImageRetrieveView.as_view(), name='image-retrieve'),
]