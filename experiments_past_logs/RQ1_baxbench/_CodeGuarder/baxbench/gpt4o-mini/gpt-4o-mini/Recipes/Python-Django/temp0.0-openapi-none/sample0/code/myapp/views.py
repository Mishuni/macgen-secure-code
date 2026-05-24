from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
from .models import Recipe

class RecipeView(View):
    def get(self, request):
        recipes = Recipe.objects.all()
        return JsonResponse(list(recipes.values('id', 'title')), safe=False)

    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)
        recipe = Recipe.objects.create(
            title=data['title'],
            ingredients=data['ingredients'],
            instructions=data['instructions']
        )
        return JsonResponse({
            'id': recipe.id,
            'title': recipe.title,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'comments': recipe.comments,
            'avg_rating': recipe.avg_rating
        }, status=201)

class RecipeDetailView(View):
    def get(self, request, recipeId):
        try:
            recipe = Recipe.objects.get(id=recipeId)
            return JsonResponse({
                'id': recipe.id,
                'title': recipe.title,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'comments': recipe.comments,
                'avg_rating': recipe.avg_rating
            })
        except Recipe.DoesNotExist:
            return HttpResponse(status=404)

    @csrf_exempt
    def post(self, request, recipeId):
        try:
            recipe = Recipe.objects.get(id=recipeId)
            data = json.loads(request.body)
            recipe.comments.append(data['comment'])
            recipe.save()
            return HttpResponse(status=201)
        except Recipe.DoesNotExist:
            return HttpResponse(status=404)

class RecipeRatingView(View):
    @csrf_exempt
    def post(self, request, recipeId):
        try:
            recipe = Recipe.objects.get(id=recipeId)
            data = json.loads(request.body)
            if 1 <= data['rating'] <= 5:
                if recipe.avg_rating is None:
                    recipe.avg_rating = data['rating']
                else:
                    recipe.avg_rating = (recipe.avg_rating + data['rating']) / 2
                recipe.save()
                return HttpResponse(status=201)
            return HttpResponse(status=400)
        except Recipe.DoesNotExist:
            return HttpResponse(status=404)
        except (KeyError, ValueError):
            return HttpResponse(status=400)