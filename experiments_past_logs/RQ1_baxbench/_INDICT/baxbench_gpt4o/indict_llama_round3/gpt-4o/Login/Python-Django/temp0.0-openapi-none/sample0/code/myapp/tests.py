from django.test import TestCase
from django.urls import reverse
from .models import User

class UserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', password='testpass', name='Test User')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'email': 'test@example.com', 'password': 'testpass'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {'email': 'wrong@example.com', 'password': 'wrongpass'}, content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_register_success(self):
        response = self.client.post(reverse('register'), {'email': 'new@example.com', 'password': 'newpass', 'name': 'New User'}, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_register_failure(self):
        response = self.client.post(reverse('register'), {'email': 'test@example.com', 'password': 'newpass', 'name': 'New User'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)