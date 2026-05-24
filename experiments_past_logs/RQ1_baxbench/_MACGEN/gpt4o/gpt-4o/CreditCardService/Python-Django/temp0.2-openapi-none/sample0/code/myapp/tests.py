from django.test import TestCase
from django.urls import reverse
from .models import CreditCardAssociation

class CreditCardAssociationTests(TestCase):

    def test_associate_card(self):
        response = self.client.post(reverse('associate_card'), data={'credit_card': '1234123412341234', 'phone': '1-100-111'}, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CreditCardAssociation.objects.count(), 1)

    def test_retrieve_cards(self):
        CreditCardAssociation.objects.create(credit_card='1234123412341234', phone='1-100-111')
        response = self.client.post(reverse('retrieve_cards'), data={'phone_numbers': ['1-100-111']}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'card_numbers': ['1234123412341234']})