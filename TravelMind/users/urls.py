from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, ProfileView, DestinationInterestedUsersView,
    FavoriteListView, FavoriteToggleView,
    WishlistListView, WishlistToggleView,
    VisitedListView, VisitedToggleView,
    GoogleAuthView,
    PasswordResetRequestView, PasswordResetConfirmView,
    VerifiedTokenObtainPairView, VerifyEmailView, ResendVerificationEmailView,
)
from .admin_views import (
    AdminUserListView, AdminUserCreateView, AdminUserDetailView, AdminSimilarUsersView,
    AdminTokenObtainPairView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', VerifiedTokenObtainPairView.as_view(), name='login'),
    path('admin/login/', AdminTokenObtainPairView.as_view(), name='admin-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path(
        'destinations/<int:destination_id>/interested/',
        DestinationInterestedUsersView.as_view(),
        name='destination-interested-users',
    ),
    path('favorites/', FavoriteListView.as_view(), name='favorites-list'),
    path('favorites/<int:pk>/', FavoriteToggleView.as_view(), name='favorites-toggle'),
    path('wishlist/', WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist/<int:pk>/', WishlistToggleView.as_view(), name='wishlist-toggle'),
    path('visited/', VisitedListView.as_view(), name='visited-list'),
    path('visited/<int:pk>/', VisitedToggleView.as_view(), name='visited-toggle'),
    path('google-auth/', GoogleAuthView.as_view(), name='google-auth'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/create/', AdminUserCreateView.as_view(), name='admin-user-create'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<int:pk>/similar/', AdminSimilarUsersView.as_view(), name='admin-similar-users'),
]
