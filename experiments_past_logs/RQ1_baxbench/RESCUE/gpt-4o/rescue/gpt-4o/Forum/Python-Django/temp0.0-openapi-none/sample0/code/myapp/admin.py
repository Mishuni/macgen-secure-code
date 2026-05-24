from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('username', 'content')