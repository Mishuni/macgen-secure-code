from django.db import models

class Entry(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.CharField(max_length=100)
    last_modified_by = models.CharField(max_length=100)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title