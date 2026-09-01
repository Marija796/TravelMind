from django.urls import path
from .views import (
    DestinationListView, DestinationDetailView, DestinationDetailBySlugView,
    AdminDestinationCreateView, AdminDestinationUpdateDeleteView,
)
from .admin_views import (
    TravelCategoryListView, SeasonListView,
    AdminTravelCategoryListCreateView, AdminTravelCategoryDetailView,
    AdminSeasonListCreateView, AdminSeasonDetailView,
)

urlpatterns = [
    path('', DestinationListView.as_view(), name='destination-list'),
    path('categories/', TravelCategoryListView.as_view(), name='travel-category-list'),
    path('seasons/', SeasonListView.as_view(), name='season-list'),
    path('admin/create/', AdminDestinationCreateView.as_view(), name='admin-destination-create'),
    path('admin/categories/', AdminTravelCategoryListCreateView.as_view(), name='admin-category-list-create'),
    path('admin/categories/<int:pk>/', AdminTravelCategoryDetailView.as_view(), name='admin-category-detail'),
    path('admin/seasons/', AdminSeasonListCreateView.as_view(), name='admin-season-list-create'),
    path('admin/seasons/<int:pk>/', AdminSeasonDetailView.as_view(), name='admin-season-detail'),
    path('admin/<int:pk>/', AdminDestinationUpdateDeleteView.as_view(), name='admin-destination-detail'),
    path('<int:pk>/', DestinationDetailView.as_view(), name='destination-detail'),
    path('by-slug/<slug:slug>/', DestinationDetailBySlugView.as_view(), name='destination-detail-by-slug'),
]
