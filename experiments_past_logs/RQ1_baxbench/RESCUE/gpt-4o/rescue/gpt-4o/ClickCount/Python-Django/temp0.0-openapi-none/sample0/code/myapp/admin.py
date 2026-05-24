from django.contrib import admin
from .models import Click

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp')