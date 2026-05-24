from django.db import models

class CardAssociation(models.Model):
    credit_card = models.CharField(max_length=16)
    phone = models.CharField(max_length=15)

    class Meta:
        unique_together = ('credit_card', 'phone')