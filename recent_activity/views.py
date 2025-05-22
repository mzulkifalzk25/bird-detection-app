from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import UserActivity, RecentActivity
from .serializers import UserActivitySerializer, RecentActivitySerializer
from core.views import BaseAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

class UserRecentActivityView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Get user's recent activities (limited to 10)",
        responses={
            200: UserActivitySerializer(many=True),
            401: "Unauthorized"
        }
    )
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
        query = self.request.query_params.get('q', '')
        return UserActivity.objects.filter(
            Q(user=self.request.user) &
            (Q(description__icontains=query) |
             Q(activity_type__icontains=query) |
             Q(location_name__icontains=query))
        )

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
