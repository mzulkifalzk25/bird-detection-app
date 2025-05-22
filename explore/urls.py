from django.urls import path
from .views import (
    ExploreView,
    BirdSearchView,
    CommonFeederBirdsView,
    BirdsByCategoryView
)

app_name = 'explore'

urlpatterns = [
    # Explore content
    path('user/explore/', ExploreView.as_view(), name='explore'),
    path('user/search/', BirdSearchView.as_view(), name='bird_search'),
    path('user/common-feeder-birds/', CommonFeederBirdsView.as_view(), name='common_feeder_birds'),
    path('user/birds-by-category/', BirdsByCategoryView.as_view(), name='birds_by_category'),
]