from django.db import models

# Create your models here.

class DistrictsModel(models.Model):
    state = models.TextField()
    district = models.TextField()
    zone = models.TextField()
    lastupdated = models.DateTimeField(auto_now=True)