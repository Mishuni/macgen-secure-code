from django.test import TestCase
from django.urls import reverse
import json

class MonitorCommandsTest(TestCase):
    def test_monitor_commands(self):
        response = self.client.post(reverse('monitor_commands'), 
                                    data=json.dumps({'command_regex': '.*'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)