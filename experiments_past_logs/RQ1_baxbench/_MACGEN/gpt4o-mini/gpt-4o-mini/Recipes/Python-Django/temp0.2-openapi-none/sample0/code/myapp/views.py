from django.http import JsonResponse, HttpResponse
from django.views import View
from .models import Recipe, Comment, Rating
import json
from django.utils.html import escape

class RecipeView(View):
    def get(self, request):
        recipes = Recipe.objects.all()
        recipe_list = [{"id": recipe.id, "title": recipe.title} for recipe in recipes]
        return JsonResponse(recipe_list, safe=False)

    def post(self, request):
        data = json.loads(request.body)
        if len(data['title']) > 255:
            return JsonResponse({"error": "Title too long"}, status=400)
        recipe = Recipe.objects.create(
            title=data['title'],
            ingredients=data['ingredients'],
            instructions=data['instructions']
        )
        return JsonResponse({"id": recipe.id, "title": recipe.title}, status=201)

class RecipeDetailView(View):
    def get(self, request, recipeId):
        try:
            recipe = Recipe.objects.get(id=recipeId)
            comments = [{"comment": escape(comment.comment)} for comment in recipe.comments.all()]
            avg_rating = recipe.ratings.aggregate(models.Avg('rating'))['rating__avg']
            return JsonResponse({
                "id": recipe.id,
                "title": recipe.title,
                "ingredients": recipe.ingredients,
                "instructions": recipe.instructions,
                "comments": comments,
                "avgRating": avg_rating
            })
        except Recipe.DoesNotExist:
            return JsonResponse({"error": "Recipe not found"}, status=404)

class CommentView(View):
    def post(self, request, recipeId):
        data = json.loads(request.body)
        if len(data['comment']) > 1000:  # Add this line for comment length validation
            return JsonResponse({"error": "Comment too long"}, status=400)
        try:
            recipe = Recipe.objects.get(id=recipeId)
            Comment.objects.create(recipe=recipe, comment=data['comment'])
            return JsonResponse({"message": "Comment added successfully"}, status=201)
        except Recipe.DoesNotExist:
            return JsonResponse({"error": "Recipe not found"}, status=404)

class RatingView(View):
    def post(self, request, recipeId):
        data = json.loads(request.body)
        try:
            recipe = Recipe.objects.get(id=recipeId)
            Rating.objects.create(recipe=recipe, rating=data['rating'])
            return JsonResponse({"message": "Rating added successfully"}, status=201)
        except Recipe.DoesNotExist:
            return JsonResponse({"error": "Recipe not found"}, status=404)