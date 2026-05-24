from django.test import TestCase

class LoggingAPITestCase(TestCase):
    def test_log_message(self):
        response = self.client.post('/log', {'message': 'Test log message'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_retrieve_logs(self):
        self.client.post('/log', {'message': 'Test log message'}, content_type='application/json')
        response = self.client.get('/logs')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test log message', response.content.decode())