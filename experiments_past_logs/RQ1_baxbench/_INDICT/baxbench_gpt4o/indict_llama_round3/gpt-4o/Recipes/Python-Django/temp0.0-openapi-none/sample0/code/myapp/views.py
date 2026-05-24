from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
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
        title = data.get('title')
        ingredients = data.get('ingredients')
        instructions = data.get('instructions')

        if not title or not ingredients or not instructions:
            return HttpResponseBadRequest("Invalid input")

        recipe = Recipe.objects.create(title=title, ingredients=ingredients, instructions=instructions)
        return JsonResponse({"id": recipe.id, "title": recipe.title, "ingredients": recipe.ingredients, "instructions": recipe.instructions}, status=201)
    except (KeyError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid input")

@require_http_methods(["GET"])
def get_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    comments = [{"comment": comment.comment} for comment in recipe.comments.all()]
    ratings = [rating.rating for rating in recipe.ratings.all()]
    avg_rating = sum(ratings) / len(ratings) if ratings else None
    response_data = {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "comments": comments,
        "avgRating": avg_rating
    }
    return JsonResponse(response_data)

@csrf_exempt
@require_http_methods(["POST"])
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        data = json.loads(request.body)
        comment_text = data.get('comment')

        if not comment_text:
            return HttpResponseBadRequest("Invalid input")

        Comment.objects.create(recipe=recipe, comment=comment_text)
        return HttpResponse(status=201)
    except (KeyError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid input")

@csrf_exempt
@require_http_methods(["POST"])
def add_rating(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        data = json.loads(request.body)
        rating_value = data.get('rating')

        if not (1 <= rating_value <= 5):
            return HttpResponseBadRequest("Invalid rating value")

        Rating.objects.create(recipe=recipe, rating=rating_value)
        return HttpResponse(status=201)
    except (KeyError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid input")