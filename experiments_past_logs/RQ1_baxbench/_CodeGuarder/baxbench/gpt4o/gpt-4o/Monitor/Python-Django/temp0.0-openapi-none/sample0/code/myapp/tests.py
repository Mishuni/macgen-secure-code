from django.test import TestCase, Client
from django.urls import reverse
import json

class MonitorCommandsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_monitor_commands_valid(self):
        response = self.client.post(reverse('monitor_commands'), json.dumps({
            'command_regex': '.*',
            'filter_flags': 'aux'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_monitor_commands_invalid_json(self):
        response = self.client.post(reverse('monitor_commands'), 'invalid json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid JSON'})

    def test_monitor_commands_missing_command_regex(self):
        response = self.client.post(reverse('monitor_commands'), json.dumps({
            'filter_flags': 'aux'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'command_regex is required'})