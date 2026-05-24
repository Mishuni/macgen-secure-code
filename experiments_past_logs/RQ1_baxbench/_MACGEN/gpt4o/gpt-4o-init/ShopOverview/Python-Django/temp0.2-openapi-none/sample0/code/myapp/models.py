from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class MerchantManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Merchants must have an email address')
        merchant = self.model(email=self.normalize_email(email), name=name)
        merchant.set_password(password)
        merchant.save(using=self._db)
        return merchant

class Merchant(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = MerchantManager()

    def __str__(self):
        return self.email

class Ware(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)

    def __str__(self):
        return self.name