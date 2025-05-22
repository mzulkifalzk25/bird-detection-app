from django.db import models
from django.conf import settings
from birds.models import Bird

class NearbySpot(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class SpotBirdSighting(models.Model):
    spot = models.ForeignKey(NearbySpot, on_delete=models.CASCADE, related_name='sightings')
    bird = models.ForeignKey(Bird, on_delete=models.CASCADE)
    sighting_date = models.DateField()
    notes = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bird.name} at {self.spot.name} on {self.sighting_date}"
