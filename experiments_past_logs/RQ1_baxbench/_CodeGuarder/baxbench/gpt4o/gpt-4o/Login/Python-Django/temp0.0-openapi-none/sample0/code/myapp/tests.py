from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'name': 'Test User'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        self.client.post(reverse('register'), {
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'name': 'Test User'
        })
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)