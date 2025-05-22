from django.urls import path
from .views import (
    UserCollectionStatsView,
    UserBraggingRightsView,
    BirdCategoriesView,
    RarityHighlightsView,
    CollectionSearchView,
    CollectionFiltersView,
    CollectionGetAllView,
    CollectionDetailsView,
    CollectionFavoriteView,
    CollectionFavoritesView,
    UserCollectionCreateView,
    UserCollectionDetailView,
    UserStreakCreateView,
    UserStreakDetailView
)

app_name = 'collection'

urlpatterns = [
    # Collection stats and highlights
    path('stats/', UserCollectionStatsView.as_view(), name='collection_stats'),
    path('bragging-rights/', UserBraggingRightsView.as_view(), name='bragging_rights'),
    path('bird-categories/', BirdCategoriesView.as_view(), name='bird_categories'),
    path('rarity-highlights/', RarityHighlightsView.as_view(), name='rarity_highlights'),

    # Collection management
    path('search/', CollectionSearchView.as_view(), name='collection_search'),
    path('filters/', CollectionFiltersView.as_view(), name='collection_filters'),
    path('get-all/', CollectionGetAllView.as_view(), name='collection_get_all'),
    path('details/<int:id>/', CollectionDetailsView.as_view(), name='collection_details'),
    path('favorite/', CollectionFavoriteView.as_view(), name='collection_favorite'),
    path('favorites/', CollectionFavoritesView.as_view(), name='collection_favorites'),

    # New CRUD URLs
    path('create/', UserCollectionCreateView.as_view(), name='collection-create'),
    path('<int:pk>/', UserCollectionDetailView.as_view(), name='collection-detail'),
    path('streak/create/', UserStreakCreateView.as_view(), name='streak-create'),
    path('streak/<int:pk>/', UserStreakDetailView.as_view(), name='streak-detail'),
]