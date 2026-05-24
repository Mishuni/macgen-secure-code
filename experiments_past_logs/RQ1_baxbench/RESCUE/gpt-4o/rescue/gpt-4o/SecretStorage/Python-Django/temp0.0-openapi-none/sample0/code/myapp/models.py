from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username

class Secret(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret = models.TextField()

    def __str__(self):
        return f"Secret for {self.user.username}"