from django.db import models
import hashlib

class Service(models.Model):
    serviceId = models.CharField(max_length=255, unique=True)
    token = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Hash the token before saving
        self.token = hashlib.sha256(self.token.encode()).hexdigest()
        super().save(*args, **kwargs)

    last_notification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.serviceId