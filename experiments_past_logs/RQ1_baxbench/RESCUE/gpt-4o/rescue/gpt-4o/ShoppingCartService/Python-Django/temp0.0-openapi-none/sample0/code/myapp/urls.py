from django.urls import path
from .views import CreateCartView, AddToCartView, RetrieveCartView

urlpatterns = [
    path("create_cart", CreateCartView.as_view(), name="create_cart"),
    path("add_to_cart", AddToCartView.as_view(), name="add_to_cart"),
    path("retrieve_cart", RetrieveCartView.as_view(), name="retrieve_cart"),
]