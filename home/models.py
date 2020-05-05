from django.db import models

# Create your models here.

class HomeModel(models.Model):
    active_cases = models.IntegerField()
    district = models.TextField()
    zone = models.TextField()