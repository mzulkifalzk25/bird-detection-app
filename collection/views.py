from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import (
    Collection, BirdCategory, CategoryBird, UserAchievement,
    UserStreak, RarityScore, UserCollection
)
from recent_activity.models import RecentActivity
from .serializers import (
    CollectionSerializer, BirdCategorySerializer, CategoryBirdSerializer,
    UserAchievementSerializer, UserStreakSerializer, RarityScoreSerializer,
    CollectionStatsSerializer, BraggingRightsSerializer,
    CollectionSearchSerializer, CollectionFilterSerializer, UserCollectionSerializer
)
from recent_activity.serializers import RecentActivitySerializer
from .services import CollectionService
from django.db.models import Count, Q
from core.permissions import IsOwnerOrReadOnly, IsOwner
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from core.views import BaseAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

class CollectionStatsView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Get statistics about user's bird collection",
        responses={
            200: openapi.Response(
                description="Collection statistics retrieved successfully",
                examples={
                    "application/json": {
                        "total_birds": 25,
                        "rarity_breakdown": {
                            "common": 15,
                            "uncommon": 7,
                            "rare": 2,
                            "very_rare": 1
                        },
                        "recent_additions": [
                            {
                                "id": 1,
                                "bird": {
                                    "id": 1,
                                    "name": "Northern Cardinal",
                                    "scientific_name": "Cardinalis cardinalis"
                                },
                                "date_added": "2024-01-01T12:00:00Z"
                            }
                        ],
                        "monthly_progress": {
                            "2024-01": 5,
                            "2023-12": 8
                        }
                    }
                }
            ),
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def get(self, request):
        """Get user's collection statistics"""
        stats = CollectionService.get_collection_stats(request.user)
        serializer = CollectionStatsSerializer(stats)
        return Response(serializer.data)

class BraggingRightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's bragging rights"""
        rights = CollectionService.get_bragging_rights(request.user)
        serializer = BraggingRightsSerializer(rights)
        return Response(serializer.data)

class BirdCategoriesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BirdCategorySerializer
    queryset = BirdCategory.objects.all()

class RarityHighlightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's rarity highlights"""
        rarity_score = RarityScore.objects.get(user=request.user)
        serializer = RarityScoreSerializer(rarity_score)
        return Response(serializer.data)

class CollectionSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Search user's collection"""
        serializer = CollectionSearchSerializer(data=request.data)
        if serializer.is_valid():
            collections = CollectionService.search_collection(
                request.user,
                serializer.validated_data
            )
            result_serializer = CollectionSerializer(collections, many=True)
            return Response(result_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CollectionFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Filter user's collection"""
        serializer = CollectionFilterSerializer(data=request.data)
        if serializer.is_valid():
            collections = CollectionService.filter_collection(
                request.user,
                serializer.validated_data['filter_type'],
                serializer.validated_data['filter_value']
            )
            result_serializer = CollectionSerializer(collections, many=True)
            return Response(result_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CollectionListView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="List all birds in user's collection",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search birds by name or scientific name",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'rarity',
                openapi.IN_QUERY,
                description="Filter by rarity (common, uncommon, rare, very_rare)",
                type=openapi.TYPE_STRING,
                enum=['common', 'uncommon', 'rare', 'very_rare']
            )
        ],
        responses={
            200: openapi.Response(
                description="List of collected birds retrieved successfully",
                examples={
                    "application/json": {
                        "count": 2,
                        "results": [
                            {
                                "id": 1,
                                "bird": {
                                    "id": 1,
                                    "name": "Northern Cardinal",
                                    "scientific_name": "Cardinalis cardinalis",
                                    "rarity": "common"
                                },
                                "date_added": "2024-01-01T12:00:00Z",
                                "location": "Central Park, New York",
                                "notes": "First sighting of the year"
                            },
                            {
                                "id": 2,
                                "bird": {
                                    "id": 2,
                                    "name": "Blue Jay",
                                    "scientific_name": "Cyanocitta cristata",
                                    "rarity": "common"
                                },
                                "date_added": "2024-01-02T12:00:00Z",
                                "location": "Riverside Park, New York",
                                "notes": "Spotted near the river"
                            }
                        ]
                    }
                }
            ),
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def get(self, request):
        try:
            search = request.query_params.get('search', '')
            rarity = request.query_params.get('rarity')
            # ... rest of the code ...
        except Exception as e:
            raise ValidationError(str(e))

class CollectionDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CollectionSerializer

    def get_object(self):
        return get_object_or_404(
            Collection,
            user=self.request.user,
            id=self.kwargs['pk']
        )

class FavoriteCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, bird_id):
        """Toggle favorite status of a bird in collection"""
        collection = get_object_or_404(
            Collection,
            user=request.user,
            bird_id=bird_id
        )
        collection.is_favorite = not collection.is_favorite
        collection.save()

        return Response({
            'status': 'favorited' if collection.is_favorite else 'unfavorited'
        })

class FavoriteCollectionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CollectionSerializer

    def get_queryset(self):
        return Collection.objects.filter(
            user=self.request.user,
            is_favorite=True
        )

class UserCollectionStatsView(BaseAPIView):
    def get(self, request):
        try:
            user = request.user
            total_birds = UserCollection.objects.filter(user=user).count()
            unique_birds = UserCollection.objects.filter(user=user).values('bird').distinct().count()

            # Get streak information
            streak = UserStreak.objects.filter(user=user).first()
            if not streak:
                streak = UserStreak.objects.create(user=user)

            # Calculate current streak
            today = timezone.now().date()
            if streak.last_sighting_date == today:
                current_streak = streak.current_streak
            elif streak.last_sighting_date == today - timedelta(days=1):
                current_streak = streak.current_streak
            else:
                current_streak = 0

            return Response({
                'total_birds': total_birds,
                'unique_birds': unique_birds,
                'current_streak': current_streak,
                'longest_streak': streak.longest_streak
            })
        except Exception as e:
            raise ValidationError(str(e))

class UserBraggingRightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_collection = UserCollection.objects.filter(user=request.user)
        user_streak = UserStreak.objects.get_or_create(user=request.user)[0]

        stats = {
            'rarest_find': self._get_rarest_find(user_collection),
            'collection_rank': self._get_collection_rank(request.user),
            'locations_explored': user_streak.locations_explored,
            'streak_status': f"{user_streak.current_streak} Days Active"
        }
        serializer = BraggingRightsSerializer(stats)
        return Response(serializer.data)

    def _get_rarest_find(self, collection):
        rarest_bird = collection.filter(bird__rarity='S').first()
        if rarest_bird:
            return "Top 5% Find"
        rarest_bird = collection.filter(bird__rarity='A').first()
        if rarest_bird:
            return "Top 10% Find"
        return "Regular Find"

    def _get_collection_rank(self, user):
        user_score = UserCollectionStatsView._calculate_collection_score(
            None, UserCollection.objects.filter(user=user)
        )
        better_users = UserCollection.objects.values('user').annotate(
            score=Count('bird')
        ).filter(score__gt=user_score).count()

        total_users = UserCollection.objects.values('user').distinct().count()
        if total_users == 0:
            return "New Collector"

        percentile = (better_users / total_users) * 100
        if percentile <= 5:
            return "Top 5%"
        elif percentile <= 10:
            return "Top 10%"
        elif percentile <= 25:
            return "Top 25%"
        return "Top 50%"

class CollectionSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return UserCollection.objects.filter(
            Q(user=self.request.user) &
            (Q(bird__name__icontains=query) |
             Q(bird__scientific_name__icontains=query) |
             Q(notes__icontains=query))
        )

class CollectionFiltersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        queryset = UserCollection.objects.filter(user=self.request.user)

        # Filter by rarity
        rarity = self.request.query_params.get('rarity')
        if rarity:
            queryset = queryset.filter(bird__rarity=rarity)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date_added__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_added__lte=end_date)

        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location_name__icontains=location)

        return queryset

class CollectionGetAllView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        return UserCollection.objects.filter(user=self.request.user)

class CollectionDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = UserCollectionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return UserCollection.objects.filter(user=self.request.user)

class CollectionFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        collection_id = request.data.get('collection_id')
        try:
            collection = UserCollection.objects.get(
                id=collection_id,
                user=request.user
            )
            collection.is_favorite = not collection.is_favorite
            collection.save()
            return Response({
                'status': 'success',
                'is_favorite': collection.is_favorite
            })
        except UserCollection.DoesNotExist:
            return Response({
                'error': 'Collection not found'
            }, status=404)

class CollectionFavoritesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        return UserCollection.objects.filter(
            user=self.request.user,
            is_favorite=True
        )

# UserCollection CRUD
class UserCollectionCreateView(CreateAPIView):
    serializer_class = UserCollectionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            collection = serializer.save(user=self.request.user)

            # Update streak
            streak, created = UserStreak.objects.get_or_create(user=self.request.user)
            today = timezone.now().date()

            if streak.last_sighting_date == today:
                pass  # Already counted today
            elif streak.last_sighting_date == today - timedelta(days=1):
                streak.current_streak += 1
                streak.longest_streak = max(streak.current_streak, streak.longest_streak)
            else:
                streak.current_streak = 1

            streak.last_sighting_date = today
            streak.save()

            return collection
        except Exception as e:
            raise ValidationError(str(e))

class UserCollectionDetailView(RetrieveAPIView):
    serializer_class = UserCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCollection.objects.filter(user=self.request.user)

class UserCollectionUpdateView(UpdateAPIView):
    serializer_class = UserCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCollection.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Partially update a bird in user's collection",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'location': openapi.Schema(type=openapi.TYPE_STRING, description='Location where the bird was spotted'),
                'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Additional notes about the sighting'),
                'is_favorite': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the bird is marked as favorite')
            },
            example={
                'location': 'Central Park, New York',
                'notes': 'Updated sighting notes',
                'is_favorite': True
            }
        ),
        responses={
            200: openapi.Response(
                description="Bird collection updated successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "bird": {
                            "id": 1,
                            "name": "Northern Cardinal",
                            "scientific_name": "Cardinalis cardinalis"
                        },
                        "date_added": "2024-01-01T12:00:00Z",
                        "location": "Central Park, New York",
                        "notes": "Updated sighting notes",
                        "is_favorite": True,
                        "user": {
                            "id": 1,
                            "username": "birdwatcher"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication credentials were not provided",
            404: "Not Found - Collection entry does not exist"
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class UserCollectionDeleteView(DestroyAPIView):
    serializer_class = UserCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCollection.objects.filter(user=self.request.user)

# UserStreak CRUD
class UserStreakCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserStreakSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserStreakDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = UserStreakSerializer

    def get_queryset(self):
        return UserStreak.objects.filter(user=self.request.user)

class CollectionEntryView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Add a bird to user's collection",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['bird'],
            properties={
                'bird': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the bird'),
                'location': openapi.Schema(type=openapi.TYPE_STRING, description='Location where the bird was spotted'),
                'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Additional notes about the sighting')
            },
            example={
                'bird': 1,
                'location': 'Central Park, New York',
                'notes': 'First sighting of the year'
            }
        ),
        responses={
            201: openapi.Response(
                description="Bird added to collection successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "bird": {
                            "id": 1,
                            "name": "Northern Cardinal",
                            "scientific_name": "Cardinalis cardinalis"
                        },
                        "date_added": "2024-01-01T12:00:00Z",
                        "location": "Central Park, New York",
                        "notes": "First sighting of the year",
                        "user": {
                            "id": 1,
                            "username": "birdwatcher"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication credentials were not provided",
            404: "Not Found - Bird does not exist"
        }
    )
    def post(self, request):
        try:
            serializer = CollectionEntrySerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)
            # ... rest of the code ...
        except Exception as e:
            raise ValidationError(str(e))
