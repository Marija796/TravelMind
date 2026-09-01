from django.urls import path
from .views import RecommendationView, RecommendationHistoryListView

urlpatterns = [
    path('', RecommendationView.as_view(), name='recommendations'),
    path('history/', RecommendationHistoryListView.as_view(), name='recommendations-history'),
]
