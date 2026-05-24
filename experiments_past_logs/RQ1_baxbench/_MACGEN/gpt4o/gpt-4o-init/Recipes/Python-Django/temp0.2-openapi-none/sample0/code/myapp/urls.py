from django.urls import path
from . import views

urlpatterns = [
    path('recipes', views.get_recipes, name='get_recipes'),
    path('recipes/upload', views.upload_recipe, name='upload_recipe'),
    path('recipes/<int:recipe_id>', views.get_recipe, name='get_recipe'),
    path('recipes/<int:recipe_id>/comments', views.add_comment, name='add_comment'),
    path('recipes/<int:recipe_id>/ratings', views.add_rating, name='add_rating'),
]