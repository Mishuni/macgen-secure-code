from django.test import TestCase
from .models import User

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create(email="test@example.com", password="password123", name="Test User")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "Test User")