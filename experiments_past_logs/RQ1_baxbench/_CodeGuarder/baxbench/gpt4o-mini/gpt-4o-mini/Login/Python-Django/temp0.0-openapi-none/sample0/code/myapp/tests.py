from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class UserAuthTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='password123'
        )

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'email': 'user@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {
            'email': 'user@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['message'], 'Invalid email or password')

    def test_registration_success(self):
        response = self.client.post(reverse('register'), {
            'email': 'newuser@example.com',
            'password': 'newUserPassword',
            'name': 'John Doe'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'Registration successful')

    def test_registration_failure(self):
        response = self.client.post(reverse('register'), {
            'email': 'user@example.com',
            'password': 'newUserPassword',
            'name': 'John Doe'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Email already in use or invalid data')