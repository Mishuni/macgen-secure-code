from django.db import models

class Entry(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    last_modified_by = models.CharField(max_length=255)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title