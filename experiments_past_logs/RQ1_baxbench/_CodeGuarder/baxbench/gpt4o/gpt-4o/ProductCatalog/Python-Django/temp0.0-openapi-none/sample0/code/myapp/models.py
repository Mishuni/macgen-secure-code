from django.db import models
from django.contrib.postgres.fields import JSONField

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    properties = JSONField()

    def __str__(self):
        return self.name