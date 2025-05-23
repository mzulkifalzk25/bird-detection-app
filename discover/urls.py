from django.urls import path
from .views import (
    BookmarkView,
    BookmarkedArticlesView,
    DiscoveryLearnView,
    ArticleDetailsView,
    ArticleCreateView,
    ArticleDetailView,
    UserBookmarkCreateView,
    UserBookmarkDetailView
)

app_name = 'discover'

urlpatterns = [
    # Bookmark management
    path('user/bookmark/', BookmarkView.as_view(), name='bookmark'),
    path('user/bookmarked-articles/', BookmarkedArticlesView.as_view(), name='bookmarked_articles'),

    # Discovery and learning
    path('user/discovery-learn/', DiscoveryLearnView.as_view(), name='discovery_learn'),
    path('user/article-details/<int:id>/', ArticleDetailsView.as_view(), name='article_details'),

    # New CRUD URLs
    path('user/articles/create/', ArticleCreateView.as_view(), name='article-create'),
    path('user/articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('user/bookmarks/create/', UserBookmarkCreateView.as_view(), name='bookmark-create'),
    path('user/bookmarks/<int:pk>/', UserBookmarkDetailView.as_view(), name='bookmark-detail'),
]