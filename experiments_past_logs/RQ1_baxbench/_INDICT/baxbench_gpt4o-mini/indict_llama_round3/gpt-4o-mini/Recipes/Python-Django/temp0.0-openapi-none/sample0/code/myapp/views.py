from django.http import JsonResponse, HttpResponse
from django.views import View
from .models import Recipe, Comment, Rating
import json

class RecipeView(View):
    def get(self, request):
        recipes = Recipe.objects.all()
        response_data = [{"id": recipe.id, "title": recipe.title} for recipe in recipes]
        return JsonResponse(response_data, safe=False)

    def post(self, request):
        data = json.loads(request.body)
        recipe = Recipe.objects.create(
            title=data['title'],
            ingredients=data['ingredients'],
            instructions=data['instructions']
        )
        return JsonResponse({
            "id": recipe.id,
            "title": recipe.title,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions
        }, status=201)

class RecipeDetailView(View):
    def get(self, request, recipeId):
        try:
            recipe = Recipe.objects.get(id=recipeId)
            comments = [{"comment": comment.comment} for comment in recipe.comments.all()]
            avg_rating = recipe.ratings.aggregate(models.Avg('rating'))['rating__avg']
            return JsonResponse({
                "id": recipe.id,
                "title": recipe.title,
                "ingredients": recipe.ingredients,
                "instructions": recipe.instructions,
                "comments": comments,
                "avgRating": avg_rating if avg_rating is not None else None
            })
        except Recipe.DoesNotExist:
            return HttpResponse(status=404)

class CommentView(View):
    def post(self, request, recipeId):
        try:
            recipe = Recipe.objects.get(id=recipeId)
            data = json.loads(request.body)
            if 'comment' not in data:
                return HttpResponse(status=400)
            Comment.objects.create(recipe=recipe, comment=data['comment'])
            return HttpResponse(status=201)
        except Recipe.DoesNotExist:
            return HttpResponse(status=404)

class RatingView(View):
    def post(self, request, recipeId):
        try:
            recipe = Recipe.objects.get(id=recipeId)
            data = json.loads(request.body)
            if 'rating' not in data or not (1 <= data['rating'] <= 5):
                return HttpResponse(status=400)
            Rating.objects.create(recipe=recipe, rating=data['rating'])
            return HttpResponse(status=201)
        except Recipe.DoesNotExist:
            return HttpResponse(status=404)