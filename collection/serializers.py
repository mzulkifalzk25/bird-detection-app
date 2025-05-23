from rest_framework import serializers
from birds.serializers import BirdListSerializer
from .models import (
    Collection, BirdCategory, CategoryBird, UserAchievement,
    UserStreak, RarityScore, UserCollection
)
from birds.serializers import BirdSerializer

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

class UserCollectionSerializer(serializers.ModelSerializer):
    bird = BirdSerializer(read_only=True)

    class Meta:
        model = UserCollection
        fields = [
            'id', 'bird', 'is_favorite', 'date_added',
            'notes', 'latitude', 'longitude', 'location_name'
        ]
        read_only_fields = ['date_added']

class CollectionStatsSerializer(serializers.Serializer):
    s_rarity_count = serializers.IntegerField()
    a_rarity_count = serializers.IntegerField()
    b_rarity_count = serializers.IntegerField()
    c_rarity_count = serializers.IntegerField()
    collection_score = serializers.IntegerField()
    rarity_index = serializers.FloatField()

class BraggingRightsSerializer(serializers.Serializer):
    rarest_find = serializers.CharField()
    collection_rank = serializers.CharField()
    locations_explored = serializers.IntegerField()
    streak_status = serializers.CharField()

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