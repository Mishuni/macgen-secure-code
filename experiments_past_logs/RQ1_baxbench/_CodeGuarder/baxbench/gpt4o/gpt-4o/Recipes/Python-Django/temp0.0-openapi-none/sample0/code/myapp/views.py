from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import Recipe, Comment, Rating
import json

@require_http_methods(["GET"])
def get_recipes(request):
    recipes = Recipe.objects.all()
    response_data = [{"id": recipe.id, "title": recipe.title} for recipe in recipes]
    return JsonResponse(response_data, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def upload_recipe(request):
    try:
        data = json.loads(request.body)
        title = data['title']
        ingredients = data['ingredients']
        instructions = data['instructions']
        recipe = Recipe.objects.create(title=title, ingredients=ingredients, instructions=instructions)
        return JsonResponse({"id": recipe.id, "title": recipe.title}, status=201)
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid input"}, status=400)

@require_http_methods(["GET"])
def get_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    response_data = {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "comments": [{"comment": comment.comment} for comment in recipe.comments.all()],
        "avgRating": recipe.ratings.aggregate(models.Avg('rating'))['rating__avg']
    }
    return JsonResponse(response_data)

@csrf_exempt
@require_http_methods(["POST"])
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        data = json.loads(request.body)
        comment_text = data['comment']
        Comment.objects.create(recipe=recipe, comment=comment_text)
        return HttpResponse(status=201)
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid input"}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def add_rating(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        data = json.loads(request.body)
        rating_value = data['rating']
        if not (1 <= rating_value <= 5):
            return JsonResponse({"error": "Invalid rating value"}, status=400)
        Rating.objects.create(recipe=recipe, rating=rating_value)
        return HttpResponse(status=201)
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid input"}, status=400)