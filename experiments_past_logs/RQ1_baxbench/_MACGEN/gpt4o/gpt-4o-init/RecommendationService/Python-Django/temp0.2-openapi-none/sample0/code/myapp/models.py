from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, related_name='products')

    def __str__(self):
        return self.product_name