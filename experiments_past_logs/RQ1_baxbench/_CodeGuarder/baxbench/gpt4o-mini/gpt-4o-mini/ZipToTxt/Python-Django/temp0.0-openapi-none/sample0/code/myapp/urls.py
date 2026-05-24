from django.urls import path
from .views import ConvertZipToTextView

urlpatterns = [
    path('', ConvertZipToTextView.as_view(), name='convert'),
]