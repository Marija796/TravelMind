from django.urls import path
from .views import RecommendationView, AnonymousRecommendationView

urlpatterns = [
    path('', RecommendationView.as_view(), name='recommendations'),
    path('anonymous/', AnonymousRecommendationView.as_view(), name='recommendations-anonymous'),
]
