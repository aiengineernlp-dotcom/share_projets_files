from django.db import models

# Create your models here.

class Movie(models.Model):
    name = models.CharField(max_length=255)
    duration = models.FloatField()
    rating = models.FloatField()
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"
