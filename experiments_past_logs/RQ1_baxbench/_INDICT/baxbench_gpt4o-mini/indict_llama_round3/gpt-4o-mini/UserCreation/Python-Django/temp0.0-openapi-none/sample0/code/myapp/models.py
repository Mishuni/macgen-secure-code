from django.db import models
from django.contrib.auth.models import User
import uuid

class UserInvitation(models.Model):
    email = models.EmailField(unique=True)
    invite_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    invite_id = models.UUIDField()