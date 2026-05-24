from django.db import models
from django.contrib.auth.models import User

class UserSecret(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret = models.TextField()

    def __str__(self):
        return f"{self.user.username}'s secret"