from rest_framework import serializers

from recent_activity.models import UserActivity
from nearby.models import NearbySpot, SpotBirdSighting
from collection.models import UserCollection, UserStreak

from .models import (
    Bird, BirdImage, BirdSound, BirdIdentification, SimilarBird,
    BirdCategory, BirdCategoryAssignment, Article, UserBookmark, AIChat
)


class BirdImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdImage
        fields = ['id', 'image_url', 'is_primary']

class BirdSoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdSound
        fields = ['id', 'sound_url', 'sound_type', 'description']

class SimilarBirdSerializer(serializers.ModelSerializer):
    similar_to_details = serializers.SerializerMethodField()

    class Meta:
        model = SimilarBird
        fields = ['id', 'similar_to', 'similarity_score', 'similar_to_details']

    def get_similar_to_details(self, obj):
        return {
            'id': obj.similar_to.id,
            'name': obj.similar_to.name,
            'scientific_name': obj.similar_to.scientific_name,
            'image_url': obj.similar_to.image_url,
            'rarity': obj.similar_to.rarity
        }

class BirdSerializer(serializers.ModelSerializer):
    images = BirdImageSerializer(many=True, read_only=True)
    sounds = BirdSoundSerializer(many=True, read_only=True)
    similar_birds = SimilarBirdSerializer(many=True, read_only=True)

    class Meta:
        model = Bird
        fields = '__all__'

class UserCollectionSerializer(serializers.ModelSerializer):
    bird_details = BirdSerializer(source='bird', read_only=True)

    class Meta:
        model = UserCollection
        fields = ['id', 'bird', 'is_favorite', 'date_added', 'featured', 'bird_details']

class UserActivitySerializer(serializers.ModelSerializer):
    bird_details = BirdSerializer(source='bird', read_only=True)

    class Meta:
        model = UserActivity
        fields = ['id', 'activity_type', 'location_name', 'latitude', 'longitude', 'created_at', 'bird_details']

class UserStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStreak
        fields = ['current_streak', 'longest_streak', 'last_activity_date', 'locations_explored']

class BirdCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdCategory
        fields = ['id', 'name', 'description', 'image_url', 'created_at']

class BirdCategoryAssignmentSerializer(serializers.ModelSerializer):
    category_details = BirdCategorySerializer(source='category', read_only=True)
    bird_details = BirdSerializer(source='bird', read_only=True)

    class Meta:
        model = BirdCategoryAssignment
        fields = ['id', 'bird', 'category', 'category_details', 'bird_details']

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class UserBookmarkSerializer(serializers.ModelSerializer):
    article_details = ArticleSerializer(source='article', read_only=True)

    class Meta:
        model = UserBookmark
        fields = ['id', 'article', 'created_at', 'article_details']

class AIChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChat
        fields = ['id', 'message', 'response', 'created_at']

class NearbySpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = NearbySpot
        fields = '__all__'

class SpotBirdSightingSerializer(serializers.ModelSerializer):
    bird_details = BirdSerializer(source='bird', read_only=True)
    spot_details = NearbySpotSerializer(source='spot', read_only=True)

    class Meta:
        model = SpotBirdSighting
        fields = ['id', 'spot', 'bird', 'sighting_date', 'notes', 'bird_details', 'spot_details']

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

class BirdListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bird
        fields = ['id', 'name', 'scientific_name', 'image_url', 'rarity']

class BirdIdentificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdIdentification
        fields = [
            'id', 'user', 'bird', 'image_url', 'sound_url',
            'identified_species', 'confidence_level', 'ai_response',
            'latitude', 'longitude', 'location_name', 'created_at'
        ]
        read_only_fields = ['user', 'bird', 'identified_species',
                           'confidence_level', 'ai_response']

class ImageEnhancementSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)

    def validate_image(self, value):
        # Add validation for image size and format if needed
        return value

class BirdIdentificationRequestSerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)
    sound = serializers.FileField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    location_name = serializers.CharField(required=False, max_length=255)

    def validate(self, data):
        print(f"Data in serializer: {data}")
        if not data.get('image') and not data.get('sound'):
            raise serializers.ValidationError(
                "Either image or sound must be provided"
            )
        return data

class BirdDetailSerializer(serializers.ModelSerializer):
    images = BirdImageSerializer(many=True, read_only=True)
    sounds = BirdSoundSerializer(many=True, read_only=True)
    similar_birds = SimilarBirdSerializer(many=True, read_only=True)
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Bird
        fields = [
            'id', 'name', 'scientific_name', 'description', 'image_url',
            'rarity', 'conservation_status', 'weight_range', 'wingspan_range',
            'length_range', 'kingdom', 'phylum', 'bird_class', 'order',
            'family', 'habitat', 'behavior', 'feeding_habits', 'breeding_info',
            'migration_pattern', 'sound_description', 'range_map_url',
            'global_distribution', 'created_at', 'updated_at', 'images',
            'sounds', 'similar_birds', 'categories'
        ]

    def get_categories(self, obj):
        category_assignments = BirdCategoryAssignment.objects.filter(bird=obj)
        return BirdCategorySerializer([ca.category for ca in category_assignments], many=True).data