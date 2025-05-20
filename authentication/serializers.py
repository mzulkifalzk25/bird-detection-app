from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import OTP

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'date_of_birth', 'location', 
                 'profile_image', 'streak_count', 'collection_score', 
                 'locations_explored', 'is_email_verified')
        read_only_fields = ('id', 'is_email_verified', 'streak_count', 
                          'collection_score', 'locations_explored')

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'name', 'password')

    def create(self, validated_data):
        name = validated_data.pop('name')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=name,
            first_name=name,
            password=validated_data['password']
        )
        return user
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class SocialAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'date_of_birth', 'location', 'profile_image')
        
    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value 