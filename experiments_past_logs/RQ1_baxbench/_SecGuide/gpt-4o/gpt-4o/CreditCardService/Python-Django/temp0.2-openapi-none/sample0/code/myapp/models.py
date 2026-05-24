from django.db import models
from cryptography.fernet import Fernet
import os

class CreditCardAssociation(models.Model):
    credit_card = models.CharField(max_length=256)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"Card associated with {self.phone}"

    def save(self, *args, **kwargs):
        self.credit_card = self.encrypt_card(self.credit_card)
        super().save(*args, **kwargs)

    @staticmethod
    def encrypt_card(card_number):
        key = os.environ['ENCRYPTION_KEY']  # Must be set in the environment
        cipher_suite = Fernet(key)
        return cipher_suite.encrypt(card_number.encode()).decode()

    @staticmethod
    def decrypt_card(encrypted_card):
        key = os.environ['ENCRYPTION_KEY']  # Must be set in the environment
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(encrypted_card.encode()).decode()