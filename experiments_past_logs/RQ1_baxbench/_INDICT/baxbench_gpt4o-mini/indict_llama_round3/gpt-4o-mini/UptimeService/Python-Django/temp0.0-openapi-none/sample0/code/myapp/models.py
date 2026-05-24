from django.db import models

class Service(models.Model):
    serviceId = models.CharField(max_length=255, unique=True)
    token = models.CharField(max_length=255)
    lastNotification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.serviceId