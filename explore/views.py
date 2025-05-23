from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from birds.models import Bird, Article
from birds.serializers import BirdListSerializer, ArticleSerializer


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
