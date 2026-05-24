from django.db import models

class FileSearch(models.Model):
    file_path = models.CharField(max_length=255)

    def __str__(self):
        return self.file_path