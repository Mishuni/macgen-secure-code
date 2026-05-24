from django.db import models
from django.contrib.auth.models import AbstractUser

class Invitation(models.Model):
    email = models.EmailField(unique=True)
    invite_id = models.CharField(max_length=100, unique=True)

class User(AbstractUser):
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, null=True, blank=True)