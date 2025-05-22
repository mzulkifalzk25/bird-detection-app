from django.urls import path
from .views import (
    UserRecentActivityView,
    UserRecentActivityViewAllView,
    UserRecentActivitySearchView,
    RecentActivityView,
    RecentActivitySearchView
)

app_name = 'recent_activity'

urlpatterns = [
    path('', UserRecentActivityView.as_view(), name='recent_activity'),
    path('all/', UserRecentActivityViewAllView.as_view(), name='recent_activity_all'),
    path('search/', UserRecentActivitySearchView.as_view(), name='recent_activity_search'),
    path('recent/', RecentActivityView.as_view(), name='recent_activities'),
    path('recent/search/', RecentActivitySearchView.as_view(), name='recent_activities_search'),
]