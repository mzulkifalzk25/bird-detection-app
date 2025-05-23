from django.urls import path
from .views import (
    EnhanceImageView, IdentifyBirdView, BirdDetailView,
    BirdListView, UserBirdIdentificationsView,
    BirdBrainAskView, BirdBrainSearchLocationView, BirdBrainChatView,
    CommonFeederBirdsView, BirdsByCategoryView
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

    path('birdbrain/ask/', BirdBrainAskView.as_view(), name='birdbrain_ask'),
    path('birdbrain/search-location/', BirdBrainSearchLocationView.as_view(), name='birdbrain_search_location'),
    path('birdbrain/chat/', BirdBrainChatView.as_view(), name='birdbrain_chat'),

    path('common-feeder/', CommonFeederBirdsView.as_view(), name='common_feeder_birds'),
    path('by-category/', BirdsByCategoryView.as_view(), name='birds_by_category'),
]