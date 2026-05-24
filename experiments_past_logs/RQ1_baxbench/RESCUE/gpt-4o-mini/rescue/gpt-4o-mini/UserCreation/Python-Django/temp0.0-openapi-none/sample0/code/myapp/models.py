from django.db import models
from django.contrib.auth.models import User as AuthUser

class Invitation(models.Model):
    email = models.EmailField(unique=True)
    invite_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.email

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE)

    def __str__(self):
        return self.username