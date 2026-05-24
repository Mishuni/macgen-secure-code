from django.urls import path
from .views import RecipeView, RecipeDetailView, CommentView, RatingView

urlpatterns = [
    path('', RecipeView.as_view(), name='recipe-list'),
    path('<str:recipeId>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('<str:recipeId>/comments', CommentView.as_view(), name='recipe-comment'),
    path('<str:recipeId>/ratings', RatingView.as_view(), name='recipe-rating'),
]