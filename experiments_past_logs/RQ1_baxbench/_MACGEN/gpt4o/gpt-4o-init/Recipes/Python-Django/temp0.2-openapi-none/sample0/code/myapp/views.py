from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Recipe, Comment, Rating
import json

def get_recipes(request):
    if request.method == 'GET':
        recipes = Recipe.objects.all()
        response_data = [{"id": recipe.id, "title": recipe.title} for recipe in recipes]
        return JsonResponse(response_data, safe=False)
    return HttpResponseBadRequest()

@csrf_exempt
def upload_recipe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data['title']
            ingredients = data['ingredients']
            instructions = data['instructions']
            recipe = Recipe.objects.create(title=title, ingredients=ingredients, instructions=instructions)
            return JsonResponse({"id": recipe.id, "title": recipe.title, "ingredients": recipe.ingredients, "instructions": recipe.instructions}, status=201)
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest()
    return HttpResponseBadRequest()

def get_recipe(request, recipe_id):
    if request.method == 'GET':
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
    return HttpResponseBadRequest()

@csrf_exempt
def add_comment(request, recipe_id):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        try:
            data = json.loads(request.body)
            comment_text = data['comment']
            Comment.objects.create(recipe=recipe, comment=comment_text)
            return HttpResponse(status=201)
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest()
    return HttpResponseBadRequest()

@csrf_exempt
def add_rating(request, recipe_id):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        try:
            data = json.loads(request.body)
            rating_value = data['rating']
            if 1 <= rating_value <= 5:
                Rating.objects.create(recipe=recipe, rating=rating_value)
                return HttpResponse(status=201)
            else:
                return HttpResponseBadRequest()
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest()
    return HttpResponseBadRequest()