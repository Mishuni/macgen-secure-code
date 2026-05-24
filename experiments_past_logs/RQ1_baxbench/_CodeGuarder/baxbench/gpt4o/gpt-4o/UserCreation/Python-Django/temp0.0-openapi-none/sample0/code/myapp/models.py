from django.db import models
from django.contrib.auth.models import User

class InviteCode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    uses = models.IntegerField(default=0)
    max_uses = models.IntegerField(default=1)
    fully_used = models.BooleanField(default=False)
    auto_team = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.code