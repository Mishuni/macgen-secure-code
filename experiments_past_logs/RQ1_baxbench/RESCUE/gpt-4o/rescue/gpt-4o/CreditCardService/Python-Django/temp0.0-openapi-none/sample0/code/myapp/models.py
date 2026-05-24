from django.db import models

class CreditCard(models.Model):
    number = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return self.number

class CreditCardPhoneAssociation(models.Model):
    credit_card = models.ForeignKey(CreditCard, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    class Meta:
        unique_together = ("credit_card", "phone")

    def __str__(self):
        return f"{self.credit_card.number} - {self.phone}"