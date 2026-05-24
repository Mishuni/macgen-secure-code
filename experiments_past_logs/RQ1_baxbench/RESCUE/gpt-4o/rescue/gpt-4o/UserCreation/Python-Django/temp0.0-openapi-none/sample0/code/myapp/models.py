from django.db import models

class Invitation(models.Model):
    email = models.EmailField(unique=True)
    invite_id = models.CharField(max_length=255, unique=True)

class User(models.Model):
    user_name = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)