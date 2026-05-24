from django.urls import path
from .views import AssociateCardView, RetrieveCardsView

urlpatterns = [
    path("associate_card", AssociateCardView.as_view(), name="associate_card"),
    path("retrieve_cards", RetrieveCardsView.as_view(), name="retrieve_cards"),
]