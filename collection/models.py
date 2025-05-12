from django.db import models
from django.conf import settings
from birds.models import Bird

class Collection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bird = models.ForeignKey(Bird, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'bird']
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.bird.name}"

class BirdCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Bird Categories'

    def __str__(self):
        return self.name

class CategoryBird(models.Model):
    category = models.ForeignKey(BirdCategory, on_delete=models.CASCADE)
    bird = models.ForeignKey(Bird, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['category', 'bird']

    def __str__(self):
        return f"{self.bird.name} in {self.category.name}"

class UserAchievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('RAREST', 'Rarest Find'),
        ('COLLECTION', 'Collection Milestone'),
        ('STREAK', 'Streak Achievement'),
        ('LOCATION', 'Location Explorer'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date_achieved = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(default=0)  # For numerical achievements
    icon_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['-date_achieved']

    def __str__(self):
        return f"{self.user.username}'s {self.title}"

class UserStreak(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Streak: {self.current_streak} days"

class RarityScore(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    s_rarity_count = models.IntegerField(default=0)
    a_rarity_count = models.IntegerField(default=0)
    b_rarity_count = models.IntegerField(default=0)
    c_rarity_count = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Rarity Score: {self.total_score}"

    def calculate_total_score(self):
        """Calculate total score based on rarity weights"""
        weights = {'S': 100, 'A': 50, 'B': 25, 'C': 10}
        self.total_score = (
            self.s_rarity_count * weights['S'] +
            self.a_rarity_count * weights['A'] +
            self.b_rarity_count * weights['B'] +
            self.c_rarity_count * weights['C']
        )
        return self.total_score

class RecentActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bird = models.ForeignKey(Bird, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)  # e.g., "identified", "added_to_collection"
    date_added = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict)  # For additional activity-specific data

    class Meta:
        ordering = ['-date_added']
        verbose_name_plural = 'Recent Activities'

    def __str__(self):
        return f"{self.user.username}'s activity: {self.activity_type} - {self.bird.name}"
