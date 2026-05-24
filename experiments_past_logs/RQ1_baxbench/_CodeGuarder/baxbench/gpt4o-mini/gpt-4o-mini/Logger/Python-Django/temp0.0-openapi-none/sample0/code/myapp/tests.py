from django.test import TestCase
from django.urls import reverse

class LoggingAPITests(TestCase):
    def test_log_message(self):
        response = self.client.post(reverse('log'), {'message': 'Test log message'})
        self.assertEqual(response.status_code, 200)

    def test_retrieve_logs(self):
        self.client.post(reverse('log'), {'message': 'Test log message'})
        response = self.client.get(reverse('logs'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test log message', response.content)