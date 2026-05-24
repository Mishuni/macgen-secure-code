from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipes_handler),
    path('/upload', views.recipes_handler),
    path('/<int:recipe_id>', views.recipe_detail_handler),
    path('/<int:recipe_id>/comments', views.comments_handler),
    path('/<int:recipe_id>/ratings', views.ratings_handler),
]