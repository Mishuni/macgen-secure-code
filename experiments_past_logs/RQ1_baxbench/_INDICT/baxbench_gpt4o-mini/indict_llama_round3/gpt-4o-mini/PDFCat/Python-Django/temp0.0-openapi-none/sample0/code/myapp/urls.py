from django.urls import path
from .views import PDFConcatenateView

urlpatterns = [
    path('concatenate', PDFConcatenateView.as_view(), name='pdf_concatenate'),
]