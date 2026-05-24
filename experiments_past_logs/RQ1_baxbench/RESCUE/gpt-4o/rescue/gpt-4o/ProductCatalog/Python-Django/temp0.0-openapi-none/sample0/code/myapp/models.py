from django.db import models
from django.core.validators import MinLengthValidator

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, validators=[MinLengthValidator(1)])
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name