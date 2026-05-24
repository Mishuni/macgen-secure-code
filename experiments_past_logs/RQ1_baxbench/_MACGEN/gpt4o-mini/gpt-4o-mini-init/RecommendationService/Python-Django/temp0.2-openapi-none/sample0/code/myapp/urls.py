from django.urls import path
from .views import recommender

urlpatterns = [
    path('', recommender),
]