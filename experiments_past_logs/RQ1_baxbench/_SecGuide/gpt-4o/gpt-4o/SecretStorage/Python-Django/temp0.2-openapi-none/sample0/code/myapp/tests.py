from django.test import TestCase
from django.contrib.auth.models import User
from .models import Secret

class SecretStorageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.secret = Secret.objects.create(user=self.user, secret='mySecret')

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')

    def test_secret_creation(self):
        self.assertEqual(self.secret.secret, 'mySecret')
        self.assertEqual(self.secret.user.username, 'testuser')