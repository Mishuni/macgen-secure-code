from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, Secret

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        User.objects.create_user(email='testuser@example.com', username='testuser', password='testpassword')
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_secret(self):
        user = User.objects.create_user(email='testuser@example.com', username='testuser', password='testpassword')
        token = jwt.encode({'email': user.email}, os.getenv('APP_SECRET', 'default_secret_key'), algorithm='HS256')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post(reverse('set_secret'), {
            'username': 'testuser',
            'secret': 'mySecret'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_secret(self):
        user = User.objects.create_user(email='testuser@example.com', username='testuser', password='testpassword')
        Secret.objects.create(user=user, secret='mySecret')
        token = jwt.encode({'email': user.email}, os.getenv('APP_SECRET', 'default_secret_key'), algorithm='HS256')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(reverse('get_secret'), {'username': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['secret'], 'mySecret')