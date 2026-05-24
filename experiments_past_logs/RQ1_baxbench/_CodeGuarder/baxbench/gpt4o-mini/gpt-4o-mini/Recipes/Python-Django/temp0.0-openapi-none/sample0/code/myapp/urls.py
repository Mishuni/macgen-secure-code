from django.urls import path
from .views import RecipeView, RecipeDetailView, RecipeRatingView

urlpatterns = [
    path('', RecipeView.as_view(), name='recipe-list'),
    path('upload', RecipeView.as_view(), name='recipe-upload'),
    path('<str:recipeId>', RecipeDetailView.as_view(), name='recipe-detail'),
    path('<str:recipeId>/comments', RecipeDetailView.as_view(), name='recipe-comment'),
    path('<str:recipeId>/ratings', RecipeRatingView.as_view(), name='recipe-rating'),
]