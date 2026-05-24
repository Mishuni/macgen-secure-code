from django.db import models

class Entry(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.CharField(max_length=255)
    last_modified_by = models.CharField(max_length=255, blank=True, null=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title