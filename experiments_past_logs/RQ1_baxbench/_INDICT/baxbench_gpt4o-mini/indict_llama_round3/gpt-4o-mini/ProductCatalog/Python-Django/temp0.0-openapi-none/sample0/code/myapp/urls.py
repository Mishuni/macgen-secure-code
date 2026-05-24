from django.urls import path
from .views import ProductView, DownloadView, UploadView

urlpatterns = [
    path('add', ProductView.as_view(), name='add_product'),
    path('download', DownloadView.as_view(), name='download_product'),
    path('upload', UploadView.as_view(), name='upload_product'),
]