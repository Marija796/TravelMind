from django.urls import path
from .views import ReviewListCreateView, AppReviewListCreateView, AppReviewMineView

urlpatterns = [
    path('app/', AppReviewListCreateView.as_view(), name='app-review-list'),
    path('app/me/', AppReviewMineView.as_view(), name='app-review-mine'),
    path('<int:destination_id>/', ReviewListCreateView.as_view(), name='review-list'),
]