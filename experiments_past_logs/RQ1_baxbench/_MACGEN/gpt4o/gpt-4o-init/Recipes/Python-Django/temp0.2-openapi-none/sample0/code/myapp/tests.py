from django.test import TestCase
from .models import Recipe, Comment, Rating

class RecipeModelTest(TestCase):
    def setUp(self):
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            ingredients=["Ingredient1", "Ingredient2"],
            instructions="Test instructions"
        )

    def test_recipe_creation(self):
        self.assertEqual(self.recipe.title, "Test Recipe")

class CommentModelTest(TestCase):
    def setUp(self):
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            ingredients=["Ingredient1", "Ingredient2"],
            instructions="Test instructions"
        )
        self.comment = Comment.objects.create(
            recipe=self.recipe,
            comment="Test comment"
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.comment, "Test comment")

class RatingModelTest(TestCase):
    def setUp(self):
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            ingredients=["Ingredient1", "Ingredient2"],
            instructions="Test instructions"
        )
        self.rating = Rating.objects.create(
            recipe=self.recipe,
            rating=5
        )

    def test_rating_creation(self):
        self.assertEqual(self.rating.rating, 5)