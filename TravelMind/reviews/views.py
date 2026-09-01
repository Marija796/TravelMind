from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from destinations.models import Destination
from .models import Review, AppReview
from .serializers import ReviewSerializer, AppReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        # 404s on a bad/deleted destination id instead of the create path's
        # unique_together check ever colliding with a plain foreign-key
        # constraint failure (opaque IntegrityError/500) on a nonexistent one.
        get_object_or_404(Destination, pk=self.kwargs.get('destination_id'))
        destination_id = self.kwargs.get('destination_id')
        return (
            Review.objects.filter(destination_id=destination_id)
            .select_related('user')
            .order_by('-created_at')
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['destination_id'] = self.kwargs.get('destination_id')
        return context

    def perform_create(self, serializer):
        get_object_or_404(Destination, pk=self.kwargs.get('destination_id'))
        serializer.save(
            user=self.request.user,
            destination_id=self.kwargs.get('destination_id')
        )


class AppReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = AppReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return AppReview.objects.select_related('user').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        stats = queryset.aggregate(avg=Avg('rating'), total=Count('id'))
        total = stats['total']
        return Response({
            'count': total,
            'average_rating': round(stats['avg'], 1) if stats['avg'] is not None else None,
            'total_reviews': total,
            'results': serializer.data,
        })


class AppReviewMineView(APIView):
    """Single endpoint for the logged-in user's own app review: fetch, create, edit, delete."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            review = request.user.app_review
        except AppReview.DoesNotExist:
            return Response(None, status=status.HTTP_200_OK)
        return Response(AppReviewSerializer(review, context={'request': request}).data)

    def post(self, request):
        serializer = AppReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_own_review(self, request):
        return get_object_or_404(AppReview, user=request.user)

    def put(self, request):
        review = self._get_own_review(request)
        serializer = AppReviewSerializer(
            review, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)

    def delete(self, request):
        review = self._get_own_review(request)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
