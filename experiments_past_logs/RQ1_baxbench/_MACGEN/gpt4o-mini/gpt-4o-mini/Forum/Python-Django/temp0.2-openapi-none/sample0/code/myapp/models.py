from django.db import models
from django.core.validators import MaxLengthValidator

class Message(models.Model):
    content = models.TextField(validators=[MaxLengthValidator(500)])
    username = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.username}: {self.content}"