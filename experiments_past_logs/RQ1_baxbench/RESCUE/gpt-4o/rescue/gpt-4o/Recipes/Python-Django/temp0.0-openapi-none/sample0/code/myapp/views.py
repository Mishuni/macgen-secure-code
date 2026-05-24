from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Recipe, Comment, Rating
import json

@csrf_exempt
def recipes_handler(request):
    if request.method == 'GET':
        recipes = Recipe.objects.all().values('id', 'title')
        return JsonResponse(list(recipes), safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data['title']
            ingredients = data['ingredients']
            instructions = data['instructions']
            recipe = Recipe.objects.create(title=title, ingredients=ingredients, instructions=instructions)
            return JsonResponse({'id': recipe.id, 'title': recipe.title}, status=201)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid input'}, status=400)

@csrf_exempt
def recipe_detail_handler(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'GET':
        return JsonResponse({
            'id': recipe.id,
            'title': recipe.title,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'comments': list(recipe.comments.values('comment')),
            'avgRating': recipe.ratings.aggregate(avg=models.Avg('rating'))['avg']
        })

@csrf_exempt
def comments_handler(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comment = data['comment']
            Comment.objects.create(recipe=recipe, comment=comment)
            return JsonResponse({'message': 'Comment added successfully'}, status=201)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid input'}, status=400)

@csrf_exempt
def ratings_handler(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rating = data['rating']
            if not (1 <= rating <= 5):
                raise ValueError
            Rating.objects.create(recipe=recipe, rating=rating)
            return JsonResponse({'message': 'Rating added successfully'}, status=201)
        except (KeyError, ValueError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid input'}, status=400)