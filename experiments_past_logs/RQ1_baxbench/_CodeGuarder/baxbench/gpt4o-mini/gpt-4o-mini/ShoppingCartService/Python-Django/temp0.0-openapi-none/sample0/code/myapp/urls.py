from django.urls import path
from .views import create_cart, add_to_cart, retrieve_cart

urlpatterns = [
    path('create_cart', create_cart, name='create_cart'),
    path('add_to_cart', add_to_cart, name='add_to_cart'),
    path('retrieve_cart', retrieve_cart, name='retrieve_cart'),
]