from django.db import models
from django.conf import settings
from birds.models import Bird

class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('identification', 'Bird Identification'),
        ('collection', 'Collection Update'),
        ('bookmark', 'Article Bookmark'),
        ('streak', 'Streak Update'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    bird = models.ForeignKey(Bird, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'recent_activity'
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_at}"

class RecentActivity(models.Model):
    ACTIVITY_TYPES = (
        ('identified', 'Bird Identified'),
        ('added_to_collection', 'Added to Collection'),
        ('removed_from_collection', 'Removed from Collection'),
        ('location_update', 'Location Updated'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recent_activities')
    bird = models.ForeignKey(Bird, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    date_added = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict)  # For additional activity-specific data

    class Meta:
        app_label = 'recent_activity'
        ordering = ['-date_added']
        verbose_name_plural = 'Recent Activities'

    def __str__(self):
        return f"{self.user.username}'s activity: {self.activity_type} - {self.bird.name}"
