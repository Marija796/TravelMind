from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, ProfileView, SimilarUsersView,
    FavoriteListView, FavoriteToggleView,
    WishlistListView, WishlistToggleView,
    VisitedListView, VisitedToggleView,
    GoogleAuthView,
    PasswordResetRequestView, PasswordResetConfirmView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('similar/', SimilarUsersView.as_view(), name='similar-users'),
    path('favorites/', FavoriteListView.as_view(), name='favorites-list'),
    path('favorites/<int:pk>/', FavoriteToggleView.as_view(), name='favorites-toggle'),
    path('wishlist/', WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist/<int:pk>/', WishlistToggleView.as_view(), name='wishlist-toggle'),
    path('visited/', VisitedListView.as_view(), name='visited-list'),
    path('visited/<int:pk>/', VisitedToggleView.as_view(), name='visited-toggle'),
    path('google-auth/', GoogleAuthView.as_view(), name='google-auth'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
