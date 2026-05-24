from django.urls import path
from .views import recipes_overview, get_recipe, add_comment, rate_recipe

urlpatterns = [
    path('', recipes_overview, name='recipes_overview'),
    path('<str:recipeId>/', get_recipe, name='get_recipe'),
    path('<str:recipeId>/comments', add_comment, name='add_comment'),
    path('<str:recipeId>/ratings', rate_recipe, name='rate_recipe'),
]