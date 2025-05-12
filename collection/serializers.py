from rest_framework import serializers
from birds.serializers import BirdListSerializer
from .models import (
    Collection, BirdCategory, CategoryBird, UserAchievement,
    UserStreak, RarityScore, RecentActivity
)

class CollectionSerializer(serializers.ModelSerializer):
    bird_details = BirdListSerializer(source='bird', read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id', 'bird', 'bird_details', 'date_added', 'location',
            'notes', 'is_favorite', 'is_featured'
        ]
        read_only_fields = ['user']

class BirdCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdCategory
        fields = ['id', 'name', 'description', 'image_url', 'created_at']

class CategoryBirdSerializer(serializers.ModelSerializer):
    bird_details = BirdListSerializer(source='bird', read_only=True)
    category_details = BirdCategorySerializer(source='category', read_only=True)

    class Meta:
        model = CategoryBird
        fields = ['id', 'category', 'bird', 'bird_details', 'category_details']

class UserAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAchievement
        fields = [
            'id', 'achievement_type', 'title', 'description',
            'date_achieved', 'value', 'icon_url'
        ]
        read_only_fields = ['user']

class UserStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStreak
        fields = [
            'current_streak', 'longest_streak',
            'last_activity_date'
        ]
        read_only_fields = ['user']

class RarityScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RarityScore
        fields = [
            's_rarity_count', 'a_rarity_count',
            'b_rarity_count', 'c_rarity_count',
            'total_score', 'last_updated'
        ]
        read_only_fields = ['user']

class RecentActivitySerializer(serializers.ModelSerializer):
    bird_details = BirdListSerializer(source='bird', read_only=True)

    class Meta:
        model = RecentActivity
        fields = [
            'id', 'bird', 'bird_details', 'activity_type',
            'date_added', 'location', 'details'
        ]
        read_only_fields = ['user']

class CollectionStatsSerializer(serializers.Serializer):
    total_birds = serializers.IntegerField()
    favorite_birds = serializers.IntegerField()
    featured_birds = serializers.IntegerField()
    locations_explored = serializers.IntegerField()
    rarity_distribution = RarityScoreSerializer()
    recent_additions = RecentActivitySerializer(many=True)

class BraggingRightsSerializer(serializers.Serializer):
    rarest_find = serializers.CharField()
    collection_rank = serializers.CharField()
    locations_explored = serializers.IntegerField()
    streak_status = serializers.CharField()
    achievements = UserAchievementSerializer(many=True)

class CollectionSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    rarity = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

class CollectionFilterSerializer(serializers.Serializer):
    filter_type = serializers.ChoiceField(
        choices=['rarity', 'region', 'season'],
        required=True
    )
    filter_value = serializers.CharField(required=True) 