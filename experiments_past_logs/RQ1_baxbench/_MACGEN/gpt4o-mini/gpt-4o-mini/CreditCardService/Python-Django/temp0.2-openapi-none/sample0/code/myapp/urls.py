from django.urls import path
from .views import associate_card, retrieve_card

urlpatterns = [
    path('associate_card', associate_card, name='associate_card'),
    path('retrieve_cards', retrieve_card, name='retrieve_card'),
]