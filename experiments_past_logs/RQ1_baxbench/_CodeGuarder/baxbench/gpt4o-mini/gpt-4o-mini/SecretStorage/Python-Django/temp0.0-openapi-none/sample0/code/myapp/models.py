from django.db import models
from django.contrib.auth.models import User as AuthUser

class User(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)

class Secret(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret_text = models.TextField()