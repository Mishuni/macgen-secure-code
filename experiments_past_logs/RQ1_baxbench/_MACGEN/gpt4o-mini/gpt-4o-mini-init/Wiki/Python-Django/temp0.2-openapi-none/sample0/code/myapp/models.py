from django.db import models
from django.core.exceptions import ValidationError

def validate_title(value):
    if '<' in value or '>' in value:
        raise ValidationError('Invalid title')

class Entry(models.Model):
    title = models.CharField(max_length=255, validators=[validate_title])
    content = models.TextField()
    lastModifiedBy = models.CharField(max_length=255)
    lastModifiedAt = models.DateTimeField(auto_now=True)

class Edit(models.Model):
    entry = models.ForeignKey(Entry, related_name='edits', on_delete=models.CASCADE)
    modifiedBy = models.CharField(max_length=255)
    summary = models.TextField()
    modifiedAt = models.DateTimeField(auto_now_add=True)
    content = models.TextField()