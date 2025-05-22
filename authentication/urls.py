from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserLogoutView,
    # GoogleSignupView,
    # GoogleLoginView,
    # AppleSignupView,
    # AppleLoginView,
    ResetPasswordView,
)

app_name = 'authentication'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('google/signup/', GoogleSignupView.as_view(), name='google_signup'),
    # path('google/login/', GoogleLoginView.as_view(), name='google_login'),
    # path('apple/signup/', AppleSignupView.as_view(), name='apple_signup'),
    # path('apple/login/', AppleLoginView.as_view(), name='apple_login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]