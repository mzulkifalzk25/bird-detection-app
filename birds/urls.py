from django.urls import path
from .views import (
    EnhanceImageView, IdentifyBirdView, BirdDetailView,
    BirdListView, UserBirdIdentificationsView,
    UserCollectionStatsView, UserBraggingRightsView,
    UserRecentActivityView, UserRecentActivityViewAllView,
    UserRecentActivitySearchView, NearbyBirdActivityView,
    NearbyBirdActivitySearchView, NearbyBirdActivityViewAllView,
    BirdBrainAskView, BirdBrainSearchLocationView, BirdBrainChatView,
    BirdCategoriesView, RarityHighlightsView, CollectionSearchView,
    CollectionFiltersView, CollectionGetAllView, CollectionDetailsView,
    CollectionFavoriteView, CollectionFavoritesView,
    BookmarkView, BookmarkedArticlesView, DiscoveryLearnView,
    ArticleDetailsView, ExploreView, BirdSearchView,
    CommonFeederBirdsView, BirdsByCategoryView,
    NearbySpotsView, NearbyBirdListView
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

    # Home module endpoints
    path('user/collection/stats/', UserCollectionStatsView.as_view(), name='collection_stats'),
    path('user/bragging-rights/', UserBraggingRightsView.as_view(), name='bragging_rights'),
    path('user/recent-activity/', UserRecentActivityView.as_view(), name='recent_activity'),
    path('user/recent-activity/view-all/', UserRecentActivityViewAllView.as_view(), name='recent_activity_all'),
    path('user/recent-activity/search/', UserRecentActivitySearchView.as_view(), name='recent_activity_search'),
    path('user/nearby-bird-activity/', NearbyBirdActivityView.as_view(), name='nearby_bird_activity'),
    path('user/nearby-bird-activity/search/', NearbyBirdActivitySearchView.as_view(), name='nearby_bird_activity_search'),
    path('user/nearby-bird-activity/view-all/', NearbyBirdActivityViewAllView.as_view(), name='nearby_bird_activity_all'),

    # BirdBrain endpoints
    path('birdbrain/ask/', BirdBrainAskView.as_view(), name='birdbrain_ask'),
    path('birdbrain/search-location/', BirdBrainSearchLocationView.as_view(), name='birdbrain_search_location'),
    path('birdbrain/chat/', BirdBrainChatView.as_view(), name='birdbrain_chat'),

    # Collection module endpoints
    path('user/bird-categories/', BirdCategoriesView.as_view(), name='bird_categories'),
    path('user/rarity-highlights/', RarityHighlightsView.as_view(), name='rarity_highlights'),
    path('user/collection/search/', CollectionSearchView.as_view(), name='collection_search'),
    path('user/collection/filters/', CollectionFiltersView.as_view(), name='collection_filters'),
    path('user/collection/get-all/', CollectionGetAllView.as_view(), name='collection_get_all'),
    path('user/collection/details/<int:id>/', CollectionDetailsView.as_view(), name='collection_details'),
    path('user/collection/favorite/', CollectionFavoriteView.as_view(), name='collection_favorite'),
    path('user/collection/favorites/', CollectionFavoritesView.as_view(), name='collection_favorites'),

    # Discover module endpoints
    path('user/bookmark/', BookmarkView.as_view(), name='bookmark'),
    path('user/bookmarked-articles/', BookmarkedArticlesView.as_view(), name='bookmarked_articles'),
    path('user/discovery-learn/', DiscoveryLearnView.as_view(), name='discovery_learn'),
    path('user/article-details/<int:id>/', ArticleDetailsView.as_view(), name='article_details'),

    # Explore module endpoints
    path('user/explore/', ExploreView.as_view(), name='explore'),
    path('user/search/', BirdSearchView.as_view(), name='bird_search'),
    path('user/common-feeder-birds/', CommonFeederBirdsView.as_view(), name='common_feeder_birds'),
    path('user/birds-by-category/', BirdsByCategoryView.as_view(), name='birds_by_category'),

    # Nearby module endpoints
    path('user/nearby-spots/', NearbySpotsView.as_view(), name='nearby_spots'),
    path('user/nearby-bird-list/', NearbyBirdListView.as_view(), name='nearby_bird_list'),
]