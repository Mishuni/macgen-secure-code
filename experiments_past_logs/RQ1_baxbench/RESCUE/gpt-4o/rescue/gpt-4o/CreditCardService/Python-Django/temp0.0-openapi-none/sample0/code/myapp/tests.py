from django.test import TestCase
from .models import CreditCard, CreditCardPhoneAssociation

class CreditCardModelTest(TestCase):
    def test_create_credit_card(self):
        card = CreditCard.objects.create(number="1234123412341234")
        self.assertEqual(card.number, "1234123412341234")

class CreditCardPhoneAssociationTest(TestCase):
    def test_create_association(self):
        card = CreditCard.objects.create(number="1234123412341234")
        association = CreditCardPhoneAssociation.objects.create(credit_card=card, phone="1-100-111")
        self.assertEqual(association.phone, "1-100-111")