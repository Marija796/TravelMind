from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        destination_id = self.kwargs.get('destination_id')
        return Review.objects.filter(destination_id=destination_id).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            destination_id=self.kwargs.get('destination_id')
        )
