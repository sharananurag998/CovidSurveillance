from django.db import models

# Create your models here.
class Video(models.Model):
    url = models.CharField(max_length=255)
    camera_name = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    district = models.TextField()
    location = models.TextField()