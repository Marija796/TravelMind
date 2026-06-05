from django.urls import path
from .views import ReviewListCreateView

urlpatterns = [
    path('<int:destination_id>/', ReviewListCreateView.as_view(), name='review-list'),
]