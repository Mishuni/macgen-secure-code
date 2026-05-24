from django.contrib import admin
from .models import Invitation, User

admin.site.register(Invitation)
admin.site.register(User)