from django.urls import path
from .views import (
    NearbySpotsView,
    NearbyBirdListView,
    NearbyBirdActivityView,
    NearbyBirdActivitySearchView,
    NearbyBirdActivityViewAllView,
    NearbySpotCreateView,
    NearbySpotDetailView,
    SpotBirdSightingCreateView,
    SpotBirdSightingDetailView
)

app_name = 'nearby'

urlpatterns = [
    # Nearby spots
    path('user/nearby-spots/', NearbySpotsView.as_view(), name='nearby_spots'),
    path('user/nearby-bird-list/', NearbyBirdListView.as_view(), name='nearby_bird_list'),

    # Nearby bird activity
    path('user/nearby-bird-activity/', NearbyBirdActivityView.as_view(), name='nearby_bird_activity'),
    path('user/nearby-bird-activity/search/', NearbyBirdActivitySearchView.as_view(), name='nearby_bird_activity_search'),
    path('user/nearby-bird-activity/view-all/', NearbyBirdActivityViewAllView.as_view(), name='nearby_bird_activity_all'),

    # New CRUD URLs
    path('user/nearby-spots/create/', NearbySpotCreateView.as_view(), name='nearby-spot-create'),
    path('user/nearby-spots/<int:pk>/', NearbySpotDetailView.as_view(), name='nearby-spot-detail'),
    path('user/nearby-sightings/create/', SpotBirdSightingCreateView.as_view(), name='nearby-sighting-create'),
    path('user/nearby-sightings/<int:pk>/', SpotBirdSightingDetailView.as_view(), name='nearby-sighting-detail'),
]