from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    profile_image = models.URLField(max_length=500, blank=True)
    is_email_verified = models.BooleanField(default=False)
    streak_count = models.IntegerField(default=0)
    last_streak_date = models.DateField(null=True, blank=True)
    collection_score = models.IntegerField(default=0)
    locations_explored = models.IntegerField(default=0)
    
    # Social auth fields
    google_id = models.CharField(max_length=255, blank=True)
    apple_id = models.CharField(max_length=255, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
    
    def __str__(self):
        return f"{self.email} - {self.otp}"
