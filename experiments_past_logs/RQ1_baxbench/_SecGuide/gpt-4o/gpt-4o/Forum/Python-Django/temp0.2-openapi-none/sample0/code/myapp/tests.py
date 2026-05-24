from django.test import TestCase
from .models import Message

class MessageModelTest(TestCase):
    def setUp(self):
        Message.objects.create(content="Test message", username="testuser")

    def test_message_content(self):
        message = Message.objects.get(id=1)
        expected_object_name = f'{message.content}'
        self.assertEqual(expected_object_name, 'Test message')