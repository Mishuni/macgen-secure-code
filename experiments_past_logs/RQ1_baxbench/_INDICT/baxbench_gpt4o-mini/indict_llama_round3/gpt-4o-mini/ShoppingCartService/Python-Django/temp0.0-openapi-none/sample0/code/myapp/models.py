from django.db import models

class Cart(models.Model):
    cart_id = models.CharField(max_length=255, unique=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    item_id = models.IntegerField()
    count = models.IntegerField(default=0)