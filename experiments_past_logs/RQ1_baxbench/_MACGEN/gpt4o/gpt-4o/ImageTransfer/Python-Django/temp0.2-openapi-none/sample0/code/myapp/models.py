from django.db import models

class Image(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    file = models.ImageField(upload_to='images/')