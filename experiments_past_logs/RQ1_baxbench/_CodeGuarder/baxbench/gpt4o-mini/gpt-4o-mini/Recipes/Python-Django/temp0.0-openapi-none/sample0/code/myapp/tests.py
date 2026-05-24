from django.test import TestCase

class RecipeAPITests(TestCase):
    def test_recipe_upload(self):
        response = self.client.post('/recipes/upload', {
            'title': 'Test Recipe',
            'ingredients': ['Ingredient 1', 'Ingredient 2'],
            'instructions': 'Test instructions.'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_get_recipes(self):
        response = self.client.get('/recipes')
        self.assertEqual(response.status_code, 200)