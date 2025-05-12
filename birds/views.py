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
