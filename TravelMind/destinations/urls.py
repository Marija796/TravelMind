from django.urls import path
from .views import DestinationListView, DestinationDetailView, DestinationDetailBySlugView

urlpatterns = [
    path('', DestinationListView.as_view(), name='destination-list'),
    path('<int:pk>/', DestinationDetailView.as_view(), name='destination-detail'),
    path('by-slug/<slug:slug>/', DestinationDetailBySlugView.as_view(), name='destination-detail-by-slug'),
]