from django.test import TestCase
from django.urls import reverse
from .models import Recipe, Comment, Rating

class RecipeTests(TestCase):

    def test_upload_recipe(self):
        response = self.client.post(reverse('upload_recipe'), {
            'title': 'Test Recipe',
            'ingredients': ['Ingredient 1', 'Ingredient 2'],
            'instructions': 'Mix ingredients.'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_get_recipes(self):
        Recipe.objects.create(title='Test Recipe', ingredients=['Ingredient 1'], instructions='Mix ingredients.')
        response = self.client.get(reverse('get_recipes'))
        self.assertEqual(response.status_code, 200)

    def test_get_recipe(self):
        recipe = Recipe.objects.create(title='Test Recipe', ingredients=['Ingredient 1'], instructions='Mix ingredients.')
        response = self.client.get(reverse('get_recipe', args=[recipe.id]))
        self.assertEqual(response.status_code, 200)

    def test_add_comment(self):
        recipe = Recipe.objects.create(title='Test Recipe', ingredients=['Ingredient 1'], instructions='Mix ingredients.')
        response = self.client.post(reverse('add_comment', args=[recipe.id]), {
            'comment': 'Great recipe!'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_add_rating(self):
        recipe = Recipe.objects.create(title='Test Recipe', ingredients=['Ingredient 1'], instructions='Mix ingredients.')
        response = self.client.post(reverse('add_rating', args=[recipe.id]), {
            'rating': 5
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)