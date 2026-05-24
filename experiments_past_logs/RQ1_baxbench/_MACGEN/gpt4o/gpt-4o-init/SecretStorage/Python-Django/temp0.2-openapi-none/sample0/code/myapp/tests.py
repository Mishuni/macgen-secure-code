from django.test import TestCase
from django.urls import reverse
from .models import User, Secret

class UserTests(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(email='test@example.com', username='testuser', password='password123')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))

class SecretTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', username='testuser', password='password123')

    def test_secret_creation(self):
        secret = Secret.objects.create(user=self.user, secret='mySecret')
        self.assertEqual(secret.secret, 'mySecret')