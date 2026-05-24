from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)

class Secret(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret_text = models.TextField()