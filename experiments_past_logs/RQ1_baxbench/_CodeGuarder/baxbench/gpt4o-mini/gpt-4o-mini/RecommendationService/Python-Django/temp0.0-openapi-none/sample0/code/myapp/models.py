from django.db import models
from taggit.managers import TaggableManager

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    tags = TaggableManager()

    def __str__(self):
        return self.product_name