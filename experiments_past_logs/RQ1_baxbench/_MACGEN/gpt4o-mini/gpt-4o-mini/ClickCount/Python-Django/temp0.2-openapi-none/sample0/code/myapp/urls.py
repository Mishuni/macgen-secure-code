from django.urls import path
from .views import ClickView

urlpatterns = [
    path('click', ClickView.as_view()),
    path('clicks', ClickView.as_view()),
]