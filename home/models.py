from django.db import models

# Create your models here.

class HomeModel(models.Model):
    state = models.TextField()
    district = models.TextField()
    zone = models.TextField()