from django.test import TestCase, Client
from django.urls import reverse

class LogTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_log_message(self):
        response = self.client.post(reverse('log_message'), {'message': 'Test log message'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Log message successful', response.json().get('message'))

    def test_retrieve_logs(self):
        self.client.post(reverse('log_message'), {'message': 'Test log message'}, content_type='application/json')
        response = self.client.get(reverse('retrieve_logs'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test log message', response.content.decode())