from django.db import models
from django.contrib.auth.hashers import make_password

class Merchant(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only hash the password when creating a new merchant
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class Ware(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)