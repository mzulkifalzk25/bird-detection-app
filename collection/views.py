from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import (
    Collection, BirdCategory, CategoryBird, UserAchievement,
    UserStreak, RarityScore, RecentActivity
)
from .serializers import (
    CollectionSerializer, BirdCategorySerializer, CategoryBirdSerializer,
    UserAchievementSerializer, UserStreakSerializer, RarityScoreSerializer,
    RecentActivitySerializer, CollectionStatsSerializer, BraggingRightsSerializer,
    CollectionSearchSerializer, CollectionFilterSerializer
)
from .services import CollectionService

# Create your views here.

class CollectionStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
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

class RecentActivityView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecentActivitySerializer
    
    def get_queryset(self):
        return RecentActivity.objects.filter(user=self.request.user)

class RecentActivitySearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecentActivitySerializer
    
    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        return RecentActivity.objects.filter(
            user=self.request.user,
            bird__name__icontains=query
        )

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

class CollectionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CollectionSerializer
    
    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

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
