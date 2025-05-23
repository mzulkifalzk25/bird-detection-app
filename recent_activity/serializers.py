from rest_framework import serializers
from .models import UserActivity, RecentActivity
from birds.serializers import BirdSerializer, BirdListSerializer

class UserActivitySerializer(serializers.ModelSerializer):
    bird = BirdSerializer(read_only=True)

    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'bird', 'description',
            'created_at', 'latitude', 'longitude', 'location_name'
        ]
        read_only_fields = ['created_at']

class RecentActivitySerializer(serializers.ModelSerializer):
    bird_details = BirdListSerializer(source='bird', read_only=True)

    class Meta:
        model = RecentActivity
        fields = [
            'id', 'bird', 'bird_details', 'activity_type',
            'date_added', 'location', 'details'
        ]
        read_only_fields = ['date_added']