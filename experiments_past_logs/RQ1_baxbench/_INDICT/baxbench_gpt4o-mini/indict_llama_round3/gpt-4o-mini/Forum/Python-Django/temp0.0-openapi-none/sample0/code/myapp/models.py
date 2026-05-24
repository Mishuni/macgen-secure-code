from django.db import models

class Message(models.Model):
    content = models.TextField()
    username = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.username}: {self.content}"