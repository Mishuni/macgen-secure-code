from django.urls import path
from .views import ConvertZipToTxtView

urlpatterns = [
    path('convert', ConvertZipToTxtView.as_view(), name='convert_zip_to_txt'),
]