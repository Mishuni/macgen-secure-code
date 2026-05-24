from django.urls import path
from .views import FileSearchView

urlpatterns = [
    path('', FileSearchView.as_view(), name='file_search'),
]