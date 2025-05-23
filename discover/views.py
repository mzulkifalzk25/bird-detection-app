from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Article, UserBookmark
from .serializers import ArticleSerializer, UserBookmarkSerializer
from core.permissions import IsOwnerOrReadOnly, IsOwner
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

# Article CRUD
class ArticleListView(ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all articles with optional filtering",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search articles by title or content",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Filter by category",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'sort',
                openapi.IN_QUERY,
                description="Sort by field (created_at, views, likes)",
                type=openapi.TYPE_STRING,
                enum=['created_at', 'views', 'likes']
            )
        ],
        responses={
            200: openapi.Response(
                description="List of articles retrieved successfully",
                examples={
                    "application/json": {
                        "count": 2,
                        "results": [
                            {
                                "id": 1,
                                "title": "Bird Watching Basics",
                                "content": "A comprehensive guide to bird watching...",
                                "category": "Beginner",
                                "author": {
                                    "id": 1,
                                    "username": "birdwatcher"
                                },
                                "created_at": "2024-01-01T12:00:00Z",
                                "views": 150,
                                "likes": 25
                            },
                            {
                                "id": 2,
                                "title": "Advanced Bird Identification",
                                "content": "Tips for identifying rare bird species...",
                                "category": "Advanced",
                                "author": {
                                    "id": 2,
                                    "username": "birdexpert"
                                },
                                "created_at": "2024-01-02T12:00:00Z",
                                "views": 100,
                                "likes": 15
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
            category = request.query_params.get('category')
            sort = request.query_params.get('sort', '-created_at')
            queryset = Article.objects.all()

            if category:
                queryset = queryset.filter(category=category)
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(content__icontains=search) |
                    Q(tags__icontains=search)
                )

            return queryset.order_by(sort)
        except Exception as e:
            raise ValidationError(str(e))

class ArticleCreateView(CreateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            return serializer.save(author=self.request.user)
        except Exception as e:
            raise ValidationError(str(e))

class ArticleDetailView(RetrieveAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific article",
        responses={
            200: openapi.Response(
                description="Article details retrieved successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Bird Watching Basics",
                        "content": "A comprehensive guide to bird watching...",
                        "category": "Beginner",
                        "author": {
                            "id": 1,
                            "username": "birdwatcher"
                        },
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z",
                        "views": 150,
                        "likes": 25,
                        "comments": [
                            {
                                "id": 1,
                                "content": "Great article!",
                                "user": {
                                    "id": 2,
                                    "username": "birdexpert"
                                },
                                "created_at": "2024-01-01T13:00:00Z"
                            }
                        ]
                    }
                }
            ),
            404: "Not Found - Article does not exist",
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def get_queryset(self):
        return Article.objects.all()

class ArticleUpdateView(UpdateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

    @swagger_auto_schema(
        operation_description="Partially update an article",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Article title'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Article content'),
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='Article category'),
                'tags': openapi.Schema(type=openapi.TYPE_STRING, description='Article tags')
            },
            example={
                'title': 'Updated Bird Watching Guide',
                'content': 'Updated content about bird watching...',
                'category': 'Beginner',
                'tags': 'birdwatching, beginners, guide'
            }
        ),
        responses={
            200: openapi.Response(
                description="Article updated successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Updated Bird Watching Guide",
                        "content": "Updated content about bird watching...",
                        "category": "Beginner",
                        "author": {
                            "id": 1,
                            "username": "birdwatcher"
                        },
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-02T12:00:00Z",
                        "views": 150,
                        "likes": 25,
                        "tags": "birdwatching, beginners, guide"
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication credentials were not provided",
            404: "Not Found - Article does not exist"
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class ArticleDeleteView(DestroyAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

# UserBookmark CRUD
class UserBookmarkCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserBookmarkSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserBookmarkDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = UserBookmarkSerializer

    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user)

class BookmarkListView(ListAPIView):
    serializer_class = UserBookmarkSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all bookmarked articles for the current user",
        responses={
            200: openapi.Response(
                description="List of bookmarked articles retrieved successfully",
                examples={
                    "application/json": {
                        "count": 2,
                        "results": [
                            {
                                "id": 1,
                                "article": {
                                    "id": 1,
                                    "title": "Bird Watching Basics",
                                    "category": "Beginner"
                                },
                                "notes": "Great reference for beginners",
                                "created_at": "2024-01-01T12:00:00Z"
                            },
                            {
                                "id": 2,
                                "article": {
                                    "id": 2,
                                    "title": "Advanced Bird Identification",
                                    "category": "Advanced"
                                },
                                "notes": "Need to study this later",
                                "created_at": "2024-01-02T12:00:00Z"
                            }
                        ]
                    }
                }
            ),
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user).order_by('-created_at')

class BookmarkCreateView(CreateAPIView):
    serializer_class = UserBookmarkSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Bookmark an article",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['article'],
            properties={
                'article': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the article to bookmark'),
                'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Personal notes about the article')
            },
            example={
                'article': 1,
                'notes': 'Great reference for beginners'
            }
        ),
        responses={
            201: openapi.Response(
                description="Article bookmarked successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "article": {
                            "id": 1,
                            "title": "Bird Watching Basics",
                            "category": "Beginner"
                        },
                        "notes": "Great reference for beginners",
                        "created_at": "2024-01-01T12:00:00Z",
                        "user": {
                            "id": 1,
                            "username": "birdwatcher"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication credentials were not provided",
            404: "Not Found - Article does not exist"
        }
    )
    def perform_create(self, serializer):
        try:
            return serializer.save(user=self.request.user)
        except Exception as e:
            raise ValidationError(str(e))

class BookmarkDetailView(RetrieveAPIView):
    serializer_class = UserBookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user)

class BookmarkUpdateView(UpdateAPIView):
    serializer_class = UserBookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Partially update a bookmark",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Personal notes about the article')
            },
            example={
                'notes': 'Updated notes about this article'
            }
        ),
        responses={
            200: openapi.Response(
                description="Bookmark updated successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "article": {
                            "id": 1,
                            "title": "Bird Watching Basics",
                            "category": "Beginner"
                        },
                        "notes": "Updated notes about this article",
                        "created_at": "2024-01-01T12:00:00Z",
                        "user": {
                            "id": 1,
                            "username": "birdwatcher"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication credentials were not provided",
            404: "Not Found - Bookmark does not exist"
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class BookmarkDeleteView(DestroyAPIView):
    serializer_class = UserBookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user)

class BookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        article_id = request.data.get('article_id')
        notes = request.data.get('notes', '')

        try:
            article = Article.objects.get(id=article_id)
            bookmark, created = UserBookmark.objects.get_or_create(
                user=request.user,
                article=article,
                defaults={'notes': notes}
            )

            if not created:
                bookmark.notes = notes
                bookmark.save()

            return Response({
                'status': 'success',
                'is_bookmarked': True,
                'notes': bookmark.notes
            })
        except Article.DoesNotExist:
            return Response({
                'error': 'Article not found'
            }, status=404)

class BookmarkedArticlesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserBookmarkSerializer

    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user)

class DiscoveryLearnView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        category = self.request.query_params.get('category')
        queryset = Article.objects.all()

        if category:
            queryset = queryset.filter(category=category)

        return queryset

class ArticleDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Check if article is bookmarked by user
        is_bookmarked = UserBookmark.objects.filter(
            user=request.user,
            article=instance
        ).exists()

        data = serializer.data
        data['is_bookmarked'] = is_bookmarked

        return Response(data)
