from django.db import models
from django.core.validators import RegexValidator

class CreditCardAssociation(models.Model):
    credit_card = models.CharField(max_length=16, validators=[
        RegexValidator(r'^\d{16}$', 'Credit card number must be 16 digits.')
    ])
    phone = models.CharField(max_length=15, validators=[
        RegexValidator(r'^\d{1,3}-\d{3}-\d{3}$', 'Phone number must be in the format "1-100-111".')
    ])

    def __str__(self):
        return f"{self.credit_card} - {self.phone}"