from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Bird(models.Model):
    RARITY_CHOICES = [
        ('S', 'S-Rarity'),
        ('A', 'A-Rarity'),
        ('B', 'B-Rarity'),
        ('C', 'C-Rarity'),
    ]
    
    CONSERVATION_STATUS_CHOICES = [
        ('EX', 'Extinct'),
        ('EW', 'Extinct in the Wild'),
        ('CR', 'Critically Endangered'),
        ('EN', 'Endangered'),
        ('VU', 'Vulnerable'),
        ('NT', 'Near Threatened'),
        ('LC', 'Least Concern'),
        ('DD', 'Data Deficient'),
    ]

    name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(max_length=500)
    rarity = models.CharField(max_length=1, choices=RARITY_CHOICES)
    conservation_status = models.CharField(max_length=2, choices=CONSERVATION_STATUS_CHOICES)
    
    # Physical characteristics
    weight_range = models.CharField(max_length=50, blank=True)  # e.g., "20-30g"
    wingspan_range = models.CharField(max_length=50, blank=True)  # e.g., "28-32 cm"
    length_range = models.CharField(max_length=50, blank=True)  # e.g., "18-22 cm"
    
    # Classification
    kingdom = models.CharField(max_length=100, default="Animalia")
    phylum = models.CharField(max_length=100, default="Chordata")
    bird_class = models.CharField(max_length=100, default="Aves")
    order = models.CharField(max_length=100)
    family = models.CharField(max_length=100)
    
    # Additional information
    habitat = models.TextField()
    behavior = models.TextField()
    feeding_habits = models.TextField()
    breeding_info = models.TextField()
    migration_pattern = models.TextField(blank=True)
    sound_description = models.TextField(blank=True)
    
    # Geographic information
    range_map_url = models.URLField(max_length=500, blank=True)
    global_distribution = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.scientific_name})"

class BirdImage(models.Model):
    bird = models.ForeignKey(Bird, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

class BirdSound(models.Model):
    bird = models.ForeignKey(Bird, related_name='sounds', on_delete=models.CASCADE)
    sound_url = models.URLField(max_length=500)
    sound_type = models.CharField(max_length=100)  # e.g., "call", "song"
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class BirdIdentification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bird = models.ForeignKey(Bird, on_delete=models.SET_NULL, null=True)
    
    # Input data
    image_url = models.URLField(max_length=500, blank=True)
    sound_url = models.URLField(max_length=500, blank=True)
    
    # AI Response
    identified_species = models.CharField(max_length=255)
    confidence_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    ai_response = models.JSONField()  # Store full AI response
    
    # Location data
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.identified_species} - {self.confidence_level}% confidence"

class SimilarBird(models.Model):
    bird = models.ForeignKey(Bird, related_name='similar_birds', on_delete=models.CASCADE)
    similar_to = models.ForeignKey(Bird, related_name='similar_to', on_delete=models.CASCADE)
    similarity_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        unique_together = ['bird', 'similar_to']

    def __str__(self):
        return f"{self.bird.name} similar to {self.similar_to.name}"
