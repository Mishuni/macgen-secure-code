from django.test import TestCase, Client
from django.urls import reverse

class CalculatorTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_calculator_valid_expression(self):
        response = self.client.post(reverse('calculator'), data={'expression': '1 + 2 * 3'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': '7'})

    def test_calculator_invalid_expression(self):
        response = self.client.post(reverse('calculator'), data={'expression': '1 + '}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_calculator_empty_expression(self):
        response = self.client.post(reverse('calculator'), data={'expression': ''}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())