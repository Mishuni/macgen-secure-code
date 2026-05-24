from django.db import models

class CreditCardPhoneAssociation(models.Model):
    credit_card = models.CharField(max_length=16, unique=True)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.credit_card} - {self.phone}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['credit_card', 'phone'], name='unique_card_phone')
        ]