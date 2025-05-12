from rest_framework import serializers
from .models import Bird, BirdImage, BirdSound, BirdIdentification, SimilarBird

class BirdImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdImage
        fields = ['id', 'image_url', 'is_primary', 'created_at']

class BirdSoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdSound
        fields = ['id', 'sound_url', 'sound_type', 'description', 'created_at']

class SimilarBirdSerializer(serializers.ModelSerializer):
    similar_bird_details = serializers.SerializerMethodField()

    class Meta:
        model = SimilarBird
        fields = ['similar_bird_details', 'similarity_score']
    
    def get_similar_bird_details(self, obj):
        return {
            'id': obj.similar_to.id,
            'name': obj.similar_to.name,
            'scientific_name': obj.similar_to.scientific_name,
            'image_url': obj.similar_to.image_url,
            'rarity': obj.similar_to.rarity
        }

class BirdDetailSerializer(serializers.ModelSerializer):
    images = BirdImageSerializer(many=True, read_only=True)
    sounds = BirdSoundSerializer(many=True, read_only=True)
    similar_birds = SimilarBirdSerializer(many=True, read_only=True)

    class Meta:
        model = Bird
        fields = [
            'id', 'name', 'scientific_name', 'description', 'image_url',
            'rarity', 'conservation_status', 'weight_range', 'wingspan_range',
            'length_range', 'kingdom', 'phylum', 'bird_class', 'order',
            'family', 'habitat', 'behavior', 'feeding_habits', 'breeding_info',
            'migration_pattern', 'sound_description', 'range_map_url',
            'global_distribution', 'images', 'sounds', 'similar_birds',
            'created_at', 'updated_at'
        ]

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
        if not data.get('image') and not data.get('sound'):
            raise serializers.ValidationError(
                "Either image or sound must be provided"
            )
        return data 