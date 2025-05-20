from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Bird, BirdIdentification
from .serializers import (
    BirdDetailSerializer, BirdListSerializer, BirdIdentificationSerializer,
    ImageEnhancementSerializer, BirdIdentificationRequestSerializer
)
from .services import BirdIdentificationService
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    BirdImage, BirdSound, BirdCategory, Article, UserCollection,
    UserActivity, UserStreak, UserBookmark, AIChat, NearbySpot, SpotBirdSighting
)
from .serializers import (
    BirdSerializer, BirdImageSerializer, BirdSoundSerializer,
    BirdCategorySerializer, ArticleSerializer, UserCollectionSerializer,
    UserActivitySerializer, UserStreakSerializer, UserBookmarkSerializer,
    CollectionStatsSerializer, BraggingRightsSerializer, NearbySpotSerializer,
    SpotBirdSightingSerializer
)

# Create your views here.

class EnhanceImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Enhance bird image using AI"""
        serializer = ImageEnhancementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                enhanced_url = BirdIdentificationService.enhance_image(
                    serializer.validated_data['image']
                )
                return Response({'enhanced_image_url': enhanced_url})
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IdentifyBirdView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Identify bird from image or sound"""
        serializer = BirdIdentificationRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                data = serializer.validated_data

                # Handle image identification
                if 'image' in data:
                    result = BirdIdentificationService.identify_bird_from_image(
                        data['image'],
                        data.get('location_name')
                    )
                # Handle sound identification
                elif 'sound' in data:
                    result = BirdIdentificationService.identify_bird_from_sound(
                        data['sound'],
                        data.get('location_name')
                    )
                else:
                    return Response(
                        {'error': 'Either image or sound must be provided'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if not result['success']:
                    return Response(
                        {'error': result['error']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                # Get or create bird in database
                bird_data = result['data']
                bird, _ = Bird.objects.get_or_create(
                    name=bird_data['identified_species'],
                    defaults={
                        'scientific_name': bird_data['scientific_name'],
                        # Add other fields as needed
                    }
                )

                # Create identification record
                identification = BirdIdentification.objects.create(
                    user=request.user,
                    bird=bird,
                    image_url=data.get('image_url', ''),
                    sound_url=data.get('sound_url', ''),
                    identified_species=bird_data['identified_species'],
                    confidence_level=float(bird_data['confidence_level']),
                    ai_response=bird_data,
                    latitude=data.get('latitude'),
                    longitude=data.get('longitude'),
                    location_name=data.get('location_name', '')
                )

                return Response(BirdIdentificationSerializer(identification).data)

            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BirdDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Bird.objects.all()
    serializer_class = BirdDetailSerializer

    def get(self, request, *args, **kwargs):
        """Get detailed information about a bird"""
        instance = self.get_object()

        # If we don't have complete information, fetch from AI
        if not instance.description or not instance.habitat:
            try:
                result = BirdIdentificationService.get_bird_details_from_ai(instance.name)
                if result['success']:
                    bird_data = result['data']
                    # Update bird information
                    for field, value in bird_data.items():
                        if hasattr(instance, field) and not getattr(instance, field):
                            setattr(instance, field, value)
                    instance.save()
            except Exception as e:
                # Continue even if AI call fails
                pass

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class BirdListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Bird.objects.all()
    serializer_class = BirdListSerializer
    filterset_fields = ['name', 'scientific_name', 'rarity']
    search_fields = ['name', 'scientific_name', 'description']
    ordering_fields = ['name', 'rarity', 'created_at']
    ordering = ['-created_at']

class UserBirdIdentificationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BirdIdentificationSerializer

    def get_queryset(self):
        """Get all bird identifications for the current user"""
        return BirdIdentification.objects.filter(user=self.request.user)

class UserCollectionStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_collection = UserCollection.objects.filter(user=request.user)
        stats = {
            's_rarity_count': user_collection.filter(bird__rarity='S').count(),
            'a_rarity_count': user_collection.filter(bird__rarity='A').count(),
            'b_rarity_count': user_collection.filter(bird__rarity='B').count(),
            'c_rarity_count': user_collection.filter(bird__rarity='C').count(),
            'collection_score': self._calculate_collection_score(user_collection),
            'rarity_index': self._calculate_rarity_index(user_collection)
        }
        serializer = CollectionStatsSerializer(stats)
        return Response(serializer.data)

    def _calculate_collection_score(self, collection):
        score_mapping = {'S': 100, 'A': 50, 'B': 25, 'C': 10}
        return sum(score_mapping[bird.bird.rarity] for bird in collection)

    def _calculate_rarity_index(self, collection):
        if not collection:
            return 0.0
        total_score = self._calculate_collection_score(collection)
        return total_score / collection.count()

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

class UserRecentActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = UserActivity.objects.filter(user=request.user)[:10]
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

class UserRecentActivityViewAllView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserActivitySerializer

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)

class UserRecentActivitySearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserActivitySerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        return UserActivity.objects.filter(
            user=self.request.user,
            bird__name__icontains=query
        )

class NearbyBirdActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get user's location from their last activity
        last_activity = UserActivity.objects.filter(
            user=request.user,
            latitude__isnull=False
        ).first()

        if not last_activity:
            return Response({
                "error": "No location data available"
            }, status=status.HTTP_400_BAD_REQUEST)

        nearby_sightings = SpotBirdSighting.objects.filter(
            spot__latitude__range=(
                last_activity.latitude - 0.1,
                last_activity.latitude + 0.1
            ),
            spot__longitude__range=(
                last_activity.longitude - 0.1,
                last_activity.longitude + 0.1
            )
        )[:10]

        serializer = SpotBirdSightingSerializer(nearby_sightings, many=True)
        return Response(serializer.data)

class NearbyBirdActivitySearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SpotBirdSightingSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        last_activity = UserActivity.objects.filter(
            user=self.request.user,
            latitude__isnull=False
        ).first()

        if not last_activity:
            return SpotBirdSighting.objects.none()

        return SpotBirdSighting.objects.filter(
            spot__latitude__range=(
                last_activity.latitude - 0.1,
                last_activity.latitude + 0.1
            ),
            spot__longitude__range=(
                last_activity.longitude - 0.1,
                last_activity.longitude + 0.1
            ),
            bird__name__icontains=query
        )

class NearbyBirdActivityViewAllView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SpotBirdSightingSerializer

    def get_queryset(self):
        last_activity = UserActivity.objects.filter(
            user=self.request.user,
            latitude__isnull=False
        ).first()

        if not last_activity:
            return SpotBirdSighting.objects.none()

        return SpotBirdSighting.objects.filter(
            spot__latitude__range=(
                last_activity.latitude - 0.1,
                last_activity.latitude + 0.1
            ),
            spot__longitude__range=(
                last_activity.longitude - 0.1,
                last_activity.longitude + 0.1
            )
        )

class BirdBrainAskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        date = request.data.get('date')
        location = request.data.get('location')
        color = request.data.get('color')
        size = request.data.get('size')
        behavior = request.data.get('behavior')

        # Here you would integrate with your AI service
        # For now, returning mock data
        response = {
            'identified_species': 'Northern Cardinal',
            'confidence_level': 85,
            'similar_species': ['Scarlet Tanager', 'Summer Tanager'],
            'additional_details': 'Based on the red coloration and size...'
        }

        return Response(response)

class BirdBrainSearchLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        location = request.query_params.get('location', '')
        # Here you would integrate with Google Geolocation API
        # For now, returning mock data
        locations = [
            {'name': 'Central Park', 'latitude': 40.7829, 'longitude': -73.9654},
            {'name': 'Prospect Park', 'latitude': 40.6602, 'longitude': -73.9690},
        ]
        return Response(locations)

class BirdBrainChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create chat entry
        chat = AIChat.objects.create(
            user=request.user,
            message=message,
            # Here you would integrate with your AI service
            response="This is a mock response from the AI chatbot."
        )

        serializer = AIChatSerializer(chat)
        return Response(serializer.data)

class BirdCategoriesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BirdCategorySerializer

    def get_queryset(self):
        user_collection = UserCollection.objects.filter(user=self.request.user)
        return BirdCategory.objects.filter(
            birdcategoryassignment__bird__in=user_collection.values('bird')
        ).distinct()

class RarityHighlightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_collection = UserCollection.objects.filter(user=request.user)
        if not user_collection.exists():
            return Response({
                "error": "No birds in collection"
            }, status=status.HTTP_404_NOT_FOUND)

        rarest_bird = user_collection.order_by('bird__rarity').first()

        highlights = {
            'regional_abundance': self._get_regional_abundance(rarest_bird),
            'conservation_status': rarest_bird.bird.conservation_status,
            'seasonal_occurrence': self._get_seasonal_occurrence(rarest_bird),
            'overall_significance': self._get_overall_significance(rarest_bird),
            'rarity_score': rarest_bird.bird.rarity
        }

        return Response(highlights)

    def _get_regional_abundance(self, collection_entry):
        rarity_messages = {
            'S': "Extremely Rare Visitor (<5 sightings annually)",
            'A': "Rare Visitor (5-20 sightings annually)",
            'B': "Uncommon Visitor (20-100 sightings annually)",
            'C': "Common Visitor (>100 sightings annually)"
        }
        return rarity_messages.get(collection_entry.bird.rarity, "Unknown")

    def _get_seasonal_occurrence(self, collection_entry):
        # This would typically be based on the bird's migration pattern
        # For now, returning a mock response
        return "Out of Normal Seasonal Range"

    def _get_overall_significance(self, collection_entry):
        if collection_entry.bird.rarity == 'S':
            return "Exceptional find with high scientific/conservation value"
        elif collection_entry.bird.rarity == 'A':
            return "Significant find with notable conservation importance"
        elif collection_entry.bird.rarity == 'B':
            return "Uncommon find with moderate conservation value"
        return "Common find with typical conservation status"

class CollectionSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        return UserCollection.objects.filter(
            user=self.request.user,
            bird__name__icontains=query
        )

class CollectionFiltersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rarity_filters = ["All", "S-Rarity", "A-Rarity", "B-Rarity", "C-Rarity"]
        region_filters = ["Asia", "Europe", "Africa", "North America"]
        season_filters = ["Winter", "Summer", "Spring", "Autumn"]

        return Response({
            "rarity_filters": rarity_filters,
            "region_filters": region_filters,
            "season_filters": season_filters
        })

class CollectionGetAllView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        return UserCollection.objects.filter(user=self.request.user)

class CollectionDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return UserCollection.objects.filter(user=self.request.user)

class CollectionFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        bird_id = request.data.get('bird_id')
        if not bird_id:
            return Response(
                {"error": "bird_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            collection_entry = UserCollection.objects.get(
                user=request.user,
                bird_id=bird_id
            )
            collection_entry.is_favorite = not collection_entry.is_favorite
            collection_entry.save()

            return Response({
                "status": "Favorited" if collection_entry.is_favorite else "Unfavorited",
                "is_favorite": collection_entry.is_favorite
            })
        except UserCollection.DoesNotExist:
            return Response(
                {"error": "Bird not found in collection"},
                status=status.HTTP_404_NOT_FOUND
            )

class CollectionFavoritesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        return UserCollection.objects.filter(
            user=self.request.user,
            is_favorite=True
        )

class BookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        article_id = request.data.get('article_id')
        if not article_id:
            return Response(
                {"error": "article_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            article = Article.objects.get(id=article_id)
            bookmark, created = UserBookmark.objects.get_or_create(
                user=request.user,
                article=article
            )

            if not created:
                bookmark.delete()
                return Response({
                    "status": "Unbookmarked",
                    "bookmarked": False
                })

            return Response({
                "status": "Bookmarked",
                "bookmarked": True
            })

        except Article.DoesNotExist:
            return Response(
                {"error": "Article not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class BookmarkedArticlesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserBookmarkSerializer

    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user)

class DiscoveryLearnView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        filter_type = self.request.query_params.get('filter', 'All')
        queryset = Article.objects.all()
        if filter_type != 'All':
            queryset = queryset.filter(category=filter_type)
        return queryset.order_by('-published_date')



class ArticleDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Add bookmark status
        data['is_bookmarked'] = UserBookmark.objects.filter(
            user=request.user,
            article=instance
        ).exists()

        return Response(data)

class ExploreView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(
            category__in=['Migration', 'Feeder Birds']
        ).order_by('-published_date')

class BirdSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BirdListSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        filter_type = self.request.query_params.get('filter', '')
        filter_value = self.request.query_params.get('value', '')

        queryset = Bird.objects.all()

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(scientific_name__icontains=query)
            )

        if filter_type and filter_value:
            if filter_type.lower() == 'rarity':
                queryset = queryset.filter(rarity__iexact=filter_value)
            elif filter_type.lower() == 'region':
                queryset = queryset.filter(global_distribution__icontains=filter_value)

        return queryset

class CommonFeederBirdsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BirdListSerializer

    def get_queryset(self):
        return Bird.objects.filter(
            behavior__icontains='feeder'
        ).order_by('name')

class BirdsByCategoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BirdListSerializer

    def get_queryset(self):
        category = self.request.query_params.get('category', '')
        if not category:
            return Bird.objects.none()

        return Bird.objects.filter(
            birdcategoryassignment__category__name=category
        ).order_by('name')

class NearbySpotsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NearbySpotSerializer

    def get_queryset(self):
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        radius = float(self.request.query_params.get('radius', 100))  # Default 100km

        if not all([latitude, longitude]):
            return NearbySpot.objects.none()

        latitude = float(latitude)
        longitude = float(longitude)

        # Simple distance calculation (this should be replaced with proper geospatial queries)
        lat_range = (latitude - radius/111, latitude + radius/111)  # 111km per degree
        lon_range = (longitude - radius/111, longitude + radius/111)

        return NearbySpot.objects.filter(
            latitude__range=lat_range,
            longitude__range=lon_range
        )

class NearbyBirdListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SpotBirdSightingSerializer

    def get_queryset(self):
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        radius = float(self.request.query_params.get('radius', 100))  # Default 100km
        time_period = self.request.query_params.get('time_period', 'all')

        if not all([latitude, longitude]):
            return SpotBirdSighting.objects.none()

        latitude = float(latitude)
        longitude = float(longitude)

        # Simple distance calculation (this should be replaced with proper geospatial queries)
        lat_range = (latitude - radius/111, latitude + radius/111)
        lon_range = (longitude - radius/111, longitude + radius/111)

        queryset = SpotBirdSighting.objects.filter(
            spot__latitude__range=lat_range,
            spot__longitude__range=lon_range
        )

        if time_period != 'all':
            if time_period == 'recent':
                recent_date = timezone.now() - timedelta(days=30)  # Last 30 days
                queryset = queryset.filter(sighting_date__gte=recent_date)

        return queryset.order_by('-sighting_date')
