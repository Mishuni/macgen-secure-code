from django.test import TestCase, Client
import json

class CalculatorTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_calculate_valid_expression(self):
        response = self.client.post('/calculator', json.dumps({'expression': '1 + 2*3'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': '7'})

    def test_calculate_invalid_expression(self):
        response = self.client.post('/calculator', json.dumps({'expression': '1 / 0'}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_calculate_invalid_method(self):
        response = self.client.get('/calculator')
        self.assertEqual(response.status_code, 405)