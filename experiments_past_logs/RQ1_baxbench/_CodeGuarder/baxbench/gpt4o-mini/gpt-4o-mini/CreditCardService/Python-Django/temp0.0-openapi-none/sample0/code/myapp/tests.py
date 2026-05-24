from django.test import TestCase
from django.urls import reverse
import json

class CreditCardPhoneAssociationTests(TestCase):
    def test_associate_card_valid(self):
        response = self.client.post(reverse('associate_card'), {
            'credit_card': '1234123412341234',
            'phone': '1-100-111'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_associate_card_invalid(self):
        response = self.client.post(reverse('associate_card'), {
            'credit_card': 'invalid_card',
            'phone': '1-100-111'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_retrieve_cards_valid(self):
        self.client.post(reverse('associate_card'), {
            'credit_card': '1234123412341234',
            'phone': '1-100-111'
        }, content_type='application/json')
        response = self.client.post(reverse('retrieve_cards'), {
            'phone_numbers': ['1-100-111']
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('card_numbers', response.json())

    def test_retrieve_cards_invalid(self):
        response = self.client.post(reverse('retrieve_cards'), {
            'phone_numbers': []
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)