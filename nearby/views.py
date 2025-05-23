from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import NearbySpot, SpotBirdSighting
from .serializers import NearbySpotSerializer, SpotBirdSightingSerializer
from core.permissions import IsOwnerOrReadOnly, IsOwner
from core.views import BaseAPIView
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# Create your views here.

# NearbySpot CRUD
class NearbySpotCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NearbySpotSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class NearbySpotDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = NearbySpotSerializer
    queryset = NearbySpot.objects.all()

    def get_queryset(self):
        return NearbySpot.objects.filter(created_by=self.request.user)

# SpotBirdSighting CRUD
class SpotBirdSightingCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SpotBirdSightingSerializer

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

class SpotBirdSightingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = SpotBirdSightingSerializer
    queryset = SpotBirdSighting.objects.all()

    def get_queryset(self):
        return SpotBirdSighting.objects.filter(reported_by=self.request.user)

class NearbySpotsView(generics.ListAPIView):
    serializer_class = NearbySpotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            latitude = float(self.request.query_params.get('latitude'))
            longitude = float(self.request.query_params.get('longitude'))
            radius = float(self.request.query_params.get('radius', 10))  # Default 10km radius
        except (TypeError, ValueError):
            raise ValidationError("Invalid latitude, longitude, or radius parameters")

        # Get all spots and filter by distance
        spots = NearbySpot.objects.all()
        nearby_spots = []

        for spot in spots:
            distance = calculate_distance(
                latitude, longitude,
                spot.latitude, spot.longitude
            )
            if distance <= radius:
                spot.distance = distance
                nearby_spots.append(spot)

        # Sort by distance
        return sorted(nearby_spots, key=lambda x: x.distance)

class NearbyBirdListView(generics.ListAPIView):
    serializer_class = SpotBirdSightingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        spot_id = self.kwargs.get('spot_id')
        if not spot_id:
            raise ValidationError("Spot ID is required")
        return SpotBirdSighting.objects.filter(spot_id=spot_id).order_by('-sighting_date')

class NearbyBirdActivityView(BaseAPIView):
    def get(self, request):
        try:
            latitude = float(request.query_params.get('latitude'))
            longitude = float(request.query_params.get('longitude'))
            radius = float(request.query_params.get('radius', 10))
        except (TypeError, ValueError):
            raise ValidationError("Invalid latitude, longitude, or radius parameters")

        # Get all sightings and filter by distance
        sightings = SpotBirdSighting.objects.filter(is_verified=True)
        nearby_sightings = []

        for sighting in sightings:
            distance = calculate_distance(
                latitude, longitude,
                sighting.spot.latitude, sighting.spot.longitude
            )
            if distance <= radius:
                sighting.distance = distance
                nearby_sightings.append(sighting)

        # Sort by distance and take top 10
        nearby_sightings = sorted(nearby_sightings, key=lambda x: x.distance)[:10]
        serializer = SpotBirdSightingSerializer(nearby_sightings, many=True)
        return Response(serializer.data)

class NearbyBirdActivitySearchView(generics.ListAPIView):
    serializer_class = SpotBirdSightingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            query = self.request.query_params.get('query', '')
            latitude = float(self.request.query_params.get('latitude'))
            longitude = float(self.request.query_params.get('longitude'))
            radius = float(self.request.query_params.get('radius', 10))
        except (TypeError, ValueError):
            raise ValidationError("Invalid latitude, longitude, or radius parameters")

        # Get all sightings matching the query
        sightings = SpotBirdSighting.objects.filter(
            Q(bird__name__icontains=query) | Q(notes__icontains=query),
            is_verified=True
        )

        # Filter by distance
        nearby_sightings = []
        for sighting in sightings:
            distance = calculate_distance(
                latitude, longitude,
                sighting.spot.latitude, sighting.spot.longitude
            )
            if distance <= radius:
                sighting.distance = distance
                nearby_sightings.append(sighting)

        # Sort by distance
        return sorted(nearby_sightings, key=lambda x: x.distance)

class NearbyBirdActivityViewAllView(generics.ListAPIView):
    serializer_class = SpotBirdSightingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            latitude = float(self.request.query_params.get('latitude'))
            longitude = float(self.request.query_params.get('longitude'))
            radius = float(self.request.query_params.get('radius', 10))
        except (TypeError, ValueError):
            raise ValidationError("Invalid latitude, longitude, or radius parameters")

        # Get all verified sightings
        sightings = SpotBirdSighting.objects.filter(is_verified=True)
        nearby_sightings = []

        for sighting in sightings:
            distance = calculate_distance(
                latitude, longitude,
                sighting.spot.latitude, sighting.spot.longitude
            )
            if distance <= radius:
                sighting.distance = distance
                nearby_sightings.append(sighting)

        # Sort by distance
        return sorted(nearby_sightings, key=lambda x: x.distance)

class NearbySpotListView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="List nearby bird watching spots",
        manual_parameters=[
            openapi.Parameter(
                'latitude',
                openapi.IN_QUERY,
                description="User's latitude",
                type=openapi.TYPE_NUMBER,
                required=True
            ),
            openapi.Parameter(
                'longitude',
                openapi.IN_QUERY,
                description="User's longitude",
                type=openapi.TYPE_NUMBER,
                required=True
            ),
            openapi.Parameter(
                'radius',
                openapi.IN_QUERY,
                description="Search radius in kilometers",
                type=openapi.TYPE_NUMBER,
                default=10
            )
        ],
        responses={
            200: openapi.Response(
                description="List of nearby spots retrieved successfully",
                examples={
                    "application/json": {
                        "count": 2,
                        "results": [
                            {
                                "id": 1,
                                "name": "Central Park",
                                "description": "A large urban park with diverse bird species",
                                "latitude": 40.7829,
                                "longitude": -73.9654,
                                "distance": 0.5,
                                "bird_count": 15
                            },
                            {
                                "id": 2,
                                "name": "Riverside Park",
                                "description": "Park along the Hudson River",
                                "latitude": 40.8021,
                                "longitude": -73.9712,
                                "distance": 1.2,
                                "bird_count": 8
                            }
                        ]
                    }
                }
            ),
            400: "Bad Request - Invalid coordinates",
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def get(self, request):
        try:
            latitude = float(request.query_params.get('latitude'))
            longitude = float(request.query_params.get('longitude'))
            radius = float(request.query_params.get('radius', 10))
            # ... rest of the code ...
        except (ValueError, TypeError):
            raise ValidationError("Invalid coordinates provided")

class NearbySpotDetailView(generics.RetrieveAPIView):
    @swagger_auto_schema(
        operation_description="Get detailed information about a specific nearby spot",
        responses={
            200: openapi.Response(
                description="Spot details retrieved successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "name": "Central Park",
                        "description": "A large urban park with diverse bird species",
                        "latitude": 40.7829,
                        "longitude": -73.9654,
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z",
                        "is_verified": True,
                        "created_by": {
                            "id": 1,
                            "username": "birdwatcher"
                        },
                        "recent_sightings": [
                            {
                                "id": 1,
                                "bird": {
                                    "id": 1,
                                    "name": "Northern Cardinal",
                                    "scientific_name": "Cardinalis cardinalis"
                                },
                                "sighting_date": "2024-01-01",
                                "reported_by": {
                                    "id": 1,
                                    "username": "birdwatcher"
                                }
                            }
                        ]
                    }
                }
            ),
            404: "Not Found - Spot does not exist",
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class SpotBirdSightingView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Report a bird sighting at a specific spot",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['spot', 'bird', 'sighting_date'],
            properties={
                'spot': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the spot'),
                'bird': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the bird'),
                'sighting_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Date of sighting'),
                'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Additional notes about the sighting'),
                'image_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the sighting image')
            },
            example={
                'spot': 1,
                'bird': 1,
                'sighting_date': '2024-01-01',
                'notes': 'Saw a pair of cardinals near the pond',
                'image_url': 'https://example.com/cardinal.jpg'
            }
        ),
        responses={
            201: openapi.Response(
                description="Bird sighting reported successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "spot": 1,
                        "bird": {
                            "id": 1,
                            "name": "Northern Cardinal",
                            "scientific_name": "Cardinalis cardinalis"
                        },
                        "sighting_date": "2024-01-01",
                        "notes": "Saw a pair of cardinals near the pond",
                        "image_url": "https://example.com/cardinal.jpg",
                        "reported_by": {
                            "id": 1,
                            "username": "birdwatcher"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication credentials were not provided",
            404: "Not Found - Spot or bird does not exist"
        }
    )
    def post(self, request):
        try:
            serializer = SpotBirdSightingSerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)
            # ... rest of the code ...
        except Exception as e:
            raise ValidationError(str(e))
