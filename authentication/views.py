from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import random
import string
from .models import User, OTP
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    SocialAuthSerializer, SendOTPSerializer, VerifyOTPSerializer,
    ResetPasswordSerializer, EditProfileSerializer
)

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        print(" Incoming signup data:", request.data)  

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
         print(" Validation errors:", serializer.errors)  

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class GoogleSignupView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SocialAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Here you would verify the token with Google
        # and get user info from Google's response
        # This is a placeholder for the actual implementation
        
        # For demo purposes, creating/getting user with dummy data
        email = "example@gmail.com"  # This would come from Google
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'is_email_verified': True,
                'google_id': 'google_id_here'  # This would come from Google
            }
        )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class AppleSignupView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SocialAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Here you would verify the token with Apple
        # and get user info from Apple's response
        # This is a placeholder for the actual implementation
        
        # For demo purposes, creating/getting user with dummy data
        email = "example@icloud.com"  # This would come from Apple
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'is_email_verified': True,
                'apple_id': 'apple_id_here'  # This would come from Apple
            }
        )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class SendOTPView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Save OTP
        OTP.objects.create(
            email=email,
            otp=otp,
            expires_at=expires_at
        )
        
        # Here you would send the OTP via email
        # This is a placeholder for the actual email sending
        
        return Response({
            'message': 'OTP sent successfully',
            'email': email
        })

class VerifyOTPView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        otp_obj = OTP.objects.filter(
            email=email,
            otp=otp,
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if not otp_obj:
            return Response(
                {'error': 'Invalid or expired OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        # Mark user email as verified if exists
        user = User.objects.filter(email=email).first()
        if user:
            user.is_email_verified = True
            user.save()
        
        return Response({'message': 'OTP verified successfully'})

class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user.set_password(password)
        user.save()
        
        return Response({'message': 'Password reset successfully'})

class EditProfileView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditProfileSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(UserSerializer(instance).data)
