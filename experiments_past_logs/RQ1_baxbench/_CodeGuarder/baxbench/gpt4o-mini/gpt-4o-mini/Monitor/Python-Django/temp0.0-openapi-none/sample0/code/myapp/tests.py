from django.test import TestCase
from django.urls import reverse
import json

class ProcessMonitorTests(TestCase):
    def test_retrieve_processes(self):
        response = self.client.post(reverse('process_monitor'), {
            'filter_flags': 'aux',
            'command_regex': 'python'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)