from rest_framework import serializers
from .models import NearbySpot, SpotBirdSighting
from birds.serializers import BirdSerializer

class NearbySpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = NearbySpot
        fields = [
            'id', 'name', 'description', 'latitude',
            'longitude', 'created_at', 'updated_at',
            'is_verified', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at']

class SpotBirdSightingSerializer(serializers.ModelSerializer):
    bird = BirdSerializer(read_only=True)
    spot = NearbySpotSerializer(read_only=True)

    class Meta:
        model = SpotBirdSighting
        fields = [
            'id', 'spot', 'bird', 'reported_by',
            'sighting_date', 'created_at', 'notes',
            'image_url', 'is_verified'
        ]
        read_only_fields = ['created_at']