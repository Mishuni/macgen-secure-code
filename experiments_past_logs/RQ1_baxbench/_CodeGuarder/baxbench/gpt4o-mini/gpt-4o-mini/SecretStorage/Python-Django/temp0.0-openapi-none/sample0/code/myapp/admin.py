from django.contrib import admin
from .models import User, Secret

admin.site.register(User)
admin.site.register(Secret)