from django.test import TestCase

class MonitorServiceTests(TestCase):
    def test_monitor_endpoint(self):
        response = self.client.post('/monitor/commands', {
            'command_regex': '.*',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)