from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, GoogleSignupView, AppleSignupView,
    SendOTPView, VerifyOTPView, ResetPasswordView, EditProfileView
)

app_name = 'authentication'

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google-signup/', GoogleSignupView.as_view(), name='google_signup'),
    path('apple-signup/', AppleSignupView.as_view(), name='apple_signup'),
    path('otp/send/', SendOTPView.as_view(), name='send_otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify_otp'),
    path('user/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('user/edit-profile/', EditProfileView.as_view(), name='edit_profile'),
] 