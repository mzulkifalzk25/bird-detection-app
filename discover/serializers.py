from rest_framework import serializers
from .models import Article, UserBookmark

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'image_url',
            'category', 'created_at', 'updated_at',
            'author', 'read_time', 'tags'
        ]
        read_only_fields = ['created_at', 'updated_at']

class UserBookmarkSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)

    class Meta:
        model = UserBookmark
        fields = ['id', 'article', 'created_at', 'notes']
        read_only_fields = ['created_at']