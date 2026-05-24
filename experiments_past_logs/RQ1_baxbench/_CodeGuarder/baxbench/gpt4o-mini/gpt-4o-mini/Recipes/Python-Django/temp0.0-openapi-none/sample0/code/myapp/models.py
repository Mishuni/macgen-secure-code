from django.db import models

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    ingredients = models.JSONField()
    instructions = models.TextField()
    comments = models.JSONField(default=list)
    avg_rating = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title