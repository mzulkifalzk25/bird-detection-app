from django.urls import path
from .views import (
    EnhanceImageView, IdentifyBirdView, BirdDetailView,
    BirdListView, UserBirdIdentificationsView
)

app_name = 'birds'

urlpatterns = [
    # Bird identification endpoints
    path('enhance/', EnhanceImageView.as_view(), name='enhance_image'),
    path('identify/', IdentifyBirdView.as_view(), name='identify_bird'),
    
    # Bird information endpoints
    path('details/<int:pk>/', BirdDetailView.as_view(), name='bird_details'),
    path('list/', BirdListView.as_view(), name='bird_list'),
    
    # User-specific endpoints
    path('identifications/', UserBirdIdentificationsView.as_view(), name='user_identifications'),
] 