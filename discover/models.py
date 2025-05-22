from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_url = models.URLField(null=True, blank=True)
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=100)
    read_time = models.IntegerField(help_text="Estimated reading time in minutes")
    tags = models.CharField(max_length=255, help_text="Comma-separated tags")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class UserBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discover_user_bookmarks')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='discover_article_bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'article')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s bookmark of {self.article.title}"
