from django.test import TestCase
from django.urls import reverse
from .models import Message

class MessageTests(TestCase):
    def setUp(self):
        Message.objects.create(content="Hello world!", username="alice")

    def test_get_messages(self):
        response = self.client.get(reverse('message-list'), {'limit': 10, 'offset': 0, 'sort': 'DESC'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello world!")

    def test_post_message(self):
        response = self.client.post(reverse('message-list'), {'content': 'New message', 'username': 'bob'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.count(), 2)