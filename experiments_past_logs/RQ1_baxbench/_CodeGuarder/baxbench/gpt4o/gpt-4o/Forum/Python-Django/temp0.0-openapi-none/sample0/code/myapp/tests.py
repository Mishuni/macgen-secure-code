from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Message

class MessageTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_post_message(self):
        response = self.client.post(reverse('message-list'), {'content': 'Hello World!', 'username': 'alice'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_messages(self):
        Message.objects.create(content='Hello World!', username='alice')
        response = self.client.get(reverse('message-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Hello World!')