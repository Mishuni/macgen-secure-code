from django.db import models

class Click(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click {self.id} at {self.timestamp}"