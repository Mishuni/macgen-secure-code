from django.test import TestCase, Client
import os

class LogMessageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.log_file_path = os.path.join(os.path.dirname(__file__), 'logs.txt')
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

    def test_log_message(self):
        response = self.client.post('/log', {'message': 'Test log message'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists(self.log_file_path))
        with open(self.log_file_path, 'r') as log_file:
            logs = log_file.readlines()
        self.assertIn('Test log message\n', logs)

    def test_retrieve_logs(self):
        self.client.post('/log', {'message': 'Test log message'}, content_type='application/json')
        response = self.client.get('/logs')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test log message', response.content.decode())

    def tearDown(self):
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)