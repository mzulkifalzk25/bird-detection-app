from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import (
    Bird, BirdIdentification, BirdImage, BirdSound, BirdCategory,
    BirdCategoryAssignment, Article, UserBookmark, AIChat
)
from collection.models import UserCollection, UserStreak
from recent_activity.models import UserActivity
from nearby.models import NearbySpot, SpotBirdSighting
from .serializers import (
    BirdDetailSerializer, BirdListSerializer, BirdIdentificationSerializer,
    ImageEnhancementSerializer, BirdIdentificationRequestSerializer,
    BirdSerializer, BirdImageSerializer, BirdSoundSerializer,
    BirdCategorySerializer, ArticleSerializer, UserCollectionSerializer,
    UserActivitySerializer, UserStreakSerializer, UserBookmarkSerializer,
    CollectionStatsSerializer, BraggingRightsSerializer, NearbySpotSerializer,
    SpotBirdSightingSerializer
)
from .services import BirdIdentificationService
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from core.views import BaseAPIView
from rest_framework.exceptions import ValidationError
import cloudinary
import cloudinary.uploader
import google.generativeai as genai
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from PIL import Image
from transformers import pipeline
import tempfile
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Create your views here.

class EnhanceImageView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Enhance a bird image using AI",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['image'],
            properties={
                'image': openapi.Schema(type=openapi.TYPE_STRING, format='binary', description='Bird image file'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Image enhanced successfully",
                examples={
                    "application/json": {
                        "enhanced_image_url": "https://example.com/enhanced_image.jpg"
                    }
                }
            ),
            400: "Bad Request - Invalid image file",
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def post(self, request):
        try:
            serializer = ImageEnhancementSerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)

            image_data = serializer.validated_data['image']

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                image_data,
                folder="bird_images",
                transformation=[
                    {'quality': 'auto:best'},
                    {'fetch_format': 'auto'}
                ]
            )

            return Response({
                'enhanced_image_url': result['secure_url']
            })
        except Exception as e:
            raise ValidationError(str(e))

class IdentifyBirdView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = BirdIdentificationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)

            data = serializer.validated_data
            identification_type = data.get('identification_type')

            image_url = ''
            sound_url = ''

            if identification_type == 'image' or (not identification_type and data.get('image')):
                # Handle image identification
                image_data = data.get('image')
                if not image_data:
                    raise ValidationError("Image is required for image identification")

                # Save the uploaded image to MEDIA_ROOT/bird_identifications/
                image_dir = os.path.join('bird_identifications')
                image_name = default_storage.save(os.path.join(image_dir, image_data.name), ContentFile(image_data.read()))
                image_url = settings.MEDIA_URL + image_name

                # Reset file pointer before reading again
                image_data.seek(0)

                # Open the image for classification
                from PIL import Image
                from transformers import pipeline
                import tempfile

                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img_file:
                    temp_img_file.write(image_data.read())
                    temp_img_path = temp_img_file.name

                img = Image.open(temp_img_path).convert("RGB")
                pipe = pipeline("image-classification", model="dennisjooo/Birds-Classifier-EfficientNetB2")
                result = pipe(img)[0]
                os.remove(temp_img_path)

                bird_name = result['label']
                confidence = float(result.get('score', 0.8)) * 100
                ai_response = result

            elif identification_type == 'sound':
                # Handle sound identification
                sound_data = data.get('sound')
                if not sound_data:
                    raise ValidationError("Sound file is required for sound identification")

                # Save the uploaded sound to MEDIA_ROOT/bird_sounds/
                sound_dir = os.path.join('bird_sounds')
                sound_name = default_storage.save(os.path.join(sound_dir, sound_data.name), ContentFile(sound_data.read()))
                sound_url = settings.MEDIA_URL + sound_name

                # Use Gemini for sound identification (existing logic)
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(
                    f"Identify this bird species from its sound. Return only the scientific name. Sound URL: {sound_url}"
                )
                bird_name = response.text.strip()
                confidence = 0.8 * 100
                ai_response = {'gemini_response': response.text}

            else:
                raise ValidationError("Invalid identification type")

            # Find or create bird
            bird, created = Bird.objects.get_or_create(
                scientific_name=bird_name,
                defaults={
                    'name': bird_name,
                    'description': 'Automatically identified bird',
                    'image_url': image_url
                }
            )

            # Create identification record
            identification = BirdIdentification.objects.create(
                user=request.user,
                bird=bird,
                image_url=image_url,
                sound_url=sound_url,
                identified_species=bird_name,
                confidence_level=confidence,
                ai_response=ai_response,
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                location_name=data.get('location_name', '')
            )

            return Response({
                'predicted_species': bird_name,
                'image_url': image_url,
                'sound_url': sound_url,
                'identification': BirdIdentificationSerializer(identification).data
            })

        except Exception as e:
            raise ValidationError(str(e))

class BirdDetailView(RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BirdSerializer

    def get_queryset(self):
        return Bird.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            raise ValidationError(str(e))

class BirdListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BirdSerializer
    @swagger_auto_schema(
        operation_description="List all birds with optional filtering",
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
                description="List of birds retrieved successfully",
                examples={
                    "application/json": {
                        "count": 2,
                        "results": [
                            {
                                "id": 1,
                                "name": "Northern Cardinal",
                                "scientific_name": "Cardinalis cardinalis",
                                "rarity": "common"
                            },
                            {
                                "id": 2,
                                "name": "Blue Jay",
                                "scientific_name": "Cyanocitta cristata",
                                "rarity": "common"
                            }
                        ]
                    }
                }
            ),
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )

    def get_queryset(self):
        try:
            queryset = Bird.objects.all()

            # Filter by name or scientific name
            search = self.request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(scientific_name__icontains=search)
                )

            # Filter by rarity
            rarity = self.request.query_params.get('rarity')
            if rarity:
                queryset = queryset.filter(rarity=rarity)

            return queryset.order_by('name')
        except Exception as e:
            raise ValidationError(str(e))

class UserBirdIdentificationsView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BirdIdentificationSerializer

    def get_queryset(self):
        return BirdIdentification.objects.filter(user=self.request.user).order_by('-created_at')

class UserCollectionStatsView(APIView):
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = UserActivity.objects.filter(user=request.user)[:10]
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

class UserRecentActivityViewAllView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserActivitySerializer

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)

class UserRecentActivitySearchView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserActivitySerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        return UserActivity.objects.filter(
            user=self.request.user,
            bird__name__icontains=query
        )

class NearbyBirdActivityView(APIView):
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BirdCategorySerializer

    def get_queryset(self):
        user_collection = UserCollection.objects.filter(user=self.request.user)
        return BirdCategory.objects.filter(
            birdcategoryassignment__bird__in=user_collection.values('bird')
        ).distinct()

class RarityHighlightsView(APIView):
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        return UserCollection.objects.filter(
            user=self.request.user,
            bird__name__icontains=query
        )

class CollectionFiltersView(APIView):
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        return UserCollection.objects.filter(user=self.request.user)

class CollectionDetailsView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return UserCollection.objects.filter(user=self.request.user)

class CollectionFavoriteView(APIView):
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserCollectionSerializer

    def get_queryset(self):
        return UserCollection.objects.filter(
            user=self.request.user,
            is_favorite=True
        )

class BookmarkView(APIView):
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserBookmarkSerializer

    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user)

class DiscoveryLearnView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        filter_type = self.request.query_params.get('filter', 'All')
        queryset = Article.objects.all()
        if filter_type != 'All':
            queryset = queryset.filter(category=filter_type)
        return queryset.order_by('-published_date')

class ArticleDetailsView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(
            category__in=['Migration', 'Feeder Birds']
        ).order_by('-published_date')

class BirdSearchView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BirdListSerializer

    def get_queryset(self):
        return Bird.objects.filter(
            behavior__icontains='feeder'
        ).order_by('name')

class BirdsByCategoryView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
