from django.test import TestCase
from .models import CreditCardAssociation

class CreditCardAssociationTests(TestCase):
    def setUp(self):
        CreditCardAssociation.objects.create(credit_card="1234123412341234", phone="1-100-111")

    def test_association_creation(self):
        association = CreditCardAssociation.objects.get(credit_card="1234123412341234")
        self.assertEqual(association.phone, "1-100-111")

    def test_unique_constraint(self):
        with self.assertRaises(Exception):
            CreditCardAssociation.objects.create(credit_card="1234123412341234", phone="1-100-111")