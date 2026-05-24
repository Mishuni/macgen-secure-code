from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Recipe
import json
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape

@require_http_methods(["GET", "POST"])
def recipes_overview(request):
    if request.method == "GET":
        recipes = Recipe.objects.all()
        response_data = [{"id": recipe.id, "title": recipe.title} for recipe in recipes]
        return JsonResponse(response_data, safe=False)

    elif request.method == "POST":
        data = json.loads(request.body)
        title = escape(data.get("title", ""))
        ingredients = data.get("ingredients", [])
        instructions = escape(data.get("instructions", ""))
        
        recipe = Recipe.objects.create(title=title, ingredients=ingredients, instructions=instructions)
        return JsonResponse({"id": recipe.id, "title": recipe.title}, status=201)

@require_http_methods(["GET"])
def get_recipe(request, recipeId):
    try:
        recipe = Recipe.objects.get(id=recipeId)
        return JsonResponse({
            "id": recipe.id,
            "title": recipe.title,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "comments": recipe.comments,
            "avgRating": recipe.avg_rating
        })
    except ObjectDoesNotExist:
        return HttpResponse(status=404)

@csrf_exempt
@require_http_methods(["POST"])
def add_comment(request, recipeId):
    try:
        recipe = Recipe.objects.get(id=recipeId)
        data = json.loads(request.body)
        comment = escape(data.get("comment", ""))
        recipe.comments.append(comment)
        recipe.save()
        return HttpResponse(status=201)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)

@csrf_exempt
@require_http_methods(["POST"])
def rate_recipe(request, recipeId):
    try:
        recipe = Recipe.objects.get(id=recipeId)
        data = json.loads(request.body)
        rating = data.get("rating")
        
        if rating is not None and 1 <= rating <= 5:
            # Update average rating logic can be added here
            recipe.avg_rating = rating  # Simplified for this example
            recipe.save()
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)