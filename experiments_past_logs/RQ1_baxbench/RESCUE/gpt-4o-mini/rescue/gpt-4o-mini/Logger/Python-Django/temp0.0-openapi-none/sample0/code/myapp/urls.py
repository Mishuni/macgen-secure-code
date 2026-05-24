from django.urls import path
from .views import LogView

urlpatterns = [
    path('log', LogView.as_view()),
    path('logs', LogView.as_view()),
]