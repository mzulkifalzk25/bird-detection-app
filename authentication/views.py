from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
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
from core.views import BaseAPIView
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'username'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password', description='User password'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            },
            example={
                'email': 'user@example.com',
                'password': 'your_password',
                'username': 'username'
            }
        ),
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "username"
                        },
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                }
            ),
            400: "Bad Request - Invalid input data"
        }
    )
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)

            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise ValidationError(str(e))

class UserLoginView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access

    @swagger_auto_schema(
        operation_description="Login with email and password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password', description='User password'),
            },
            example={
                'email': 'user@example.com',
                'password': 'your_password'
            }
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "username"
                        },
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                }
            ),
            400: "Bad Request - Invalid credentials"
        }
    )
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                raise ValidationError("Email and password are required")

            user = authenticate(email=email, password=password)
            if not user:
                raise ValidationError("Invalid email or password")

            refresh = RefreshToken.for_user(user)

            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        except Exception as e:
            raise ValidationError(str(e))

class UserProfileView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get user profile information",
        responses={
            200: openapi.Response(
                description="User profile retrieved successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "username",
                        "bio": "Bird watching enthusiast",
                        "profile_picture": "https://example.com/profile.jpg"
                    }
                }
            ),
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            raise ValidationError(str(e))

    @swagger_auto_schema(
        operation_description="Update user profile information",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='New username'),
                'bio': openapi.Schema(type=openapi.TYPE_STRING, description='User bio'),
                'profile_picture': openapi.Schema(type=openapi.TYPE_STRING, format='binary', description='Profile picture'),
            },
            example={
                'username': 'new_username',
                'bio': 'Bird watching enthusiast'
            }
        ),
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "new_username",
                        "bio": "Bird watching enthusiast",
                        "profile_picture": "https://example.com/profile.jpg"
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def patch(self, request):
        try:
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)

            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            raise ValidationError(str(e))

class UserLogoutView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Logout user and invalidate refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to invalidate'),
            },
            example={
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            }
        ),
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={
                    "application/json": {
                        "detail": "Successfully logged out."
                    }
                }
            ),
            400: "Bad Request - Invalid refresh token",
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                raise ValidationError("Refresh token is required")

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."})
        except Exception as e:
            raise ValidationError(str(e))

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

    @swagger_auto_schema(
        operation_description="Partially update user profile",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='New username'),
                'bio': openapi.Schema(type=openapi.TYPE_STRING, description='User bio'),
                'profile_picture': openapi.Schema(type=openapi.TYPE_STRING, format='binary', description='Profile picture')
            },
            example={
                'username': 'new_username',
                'bio': 'Updated bio about bird watching'
            }
        ),
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "new_username",
                        "bio": "Updated bio about bird watching",
                        "profile_picture": "https://example.com/profile.jpg"
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication credentials were not provided"
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
