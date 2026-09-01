"""Cross-app admin statistics endpoint - lives in core since it aggregates
across users/destinations/reviews rather than belonging to any one app."""
from django.db.models import Avg, Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsAdminRole


class AdminStatsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        from users.models import CustomUser
        from destinations.models import Destination, SearchLog
        from reviews.models import Review, AppReview

        user_count = CustomUser.objects.count()
        active_user_count = CustomUser.objects.filter(is_active=True).count()
        inactive_user_count = user_count - active_user_count
        admin_count = CustomUser.objects.filter(role='admin').count()
        destination_count = Destination.objects.count()

        review_stats = Review.objects.aggregate(avg=Avg('rating'), total=Count('id'))
        app_review_stats = AppReview.objects.aggregate(avg=Avg('rating'), total=Count('id'))

        most_popular = list(
            Destination.objects.annotate(review_count_annotated=Count('reviews'))
            .order_by('-review_count_annotated', '-popularity_score')
            .values('id', 'name', 'slug', 'review_count_annotated')[:5]
        )

        # Most common travel type / season *among users' own preferences*
        # (what people are actually looking for), not among destinations -
        # a genuinely different, more useful signal for "what should we add
        # more of" than counting destinations we already have.
        most_common_travel_types = list(
            CustomUser.objects.exclude(preferred_travel_type__isnull=True)
            .values('preferred_travel_type__slug', 'preferred_travel_type__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        most_popular_seasons = list(
            CustomUser.objects.exclude(preferred_season__isnull=True)
            .values('preferred_season__slug', 'preferred_season__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        # Eligible for the Similar Users algorithm - see
        # users.views._compute_similar_users' has_preferences guard, which
        # uses this exact condition to decide the empty state.
        users_with_preferences_count = CustomUser.objects.filter(
            Q(preferred_travel_type__isnull=False) | Q(preferred_season__isnull=False)
            | Q(budget__isnull=False) | Q(trip_duration_preference__isnull=False)
            | Q(favorite_destinations__isnull=False)
        ).distinct().count()

        # Real search activity (SearchLog is written by
        # DestinationListView.list() on every non-empty search) - never
        # hardcoded/fabricated.
        most_searched = list(
            SearchLog.objects.values('query')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        return Response({
            'user_count': user_count,
            'active_user_count': active_user_count,
            'inactive_user_count': inactive_user_count,
            'admin_count': admin_count,
            'destination_count': destination_count,
            'average_destination_rating': round(review_stats['avg'], 2) if review_stats['avg'] else None,
            'total_destination_reviews': review_stats['total'],
            'average_app_rating': round(app_review_stats['avg'], 2) if app_review_stats['avg'] else None,
            'total_app_reviews': app_review_stats['total'],
            'most_popular_destinations': most_popular,
            'most_common_travel_types': [
                {'slug': r['preferred_travel_type__slug'], 'name': r['preferred_travel_type__name'], 'count': r['count']}
                for r in most_common_travel_types
            ],
            'most_popular_seasons': [
                {'slug': r['preferred_season__slug'], 'name': r['preferred_season__name'], 'count': r['count']}
                for r in most_popular_seasons
            ],
            'users_with_preferences_count': users_with_preferences_count,
            'most_searched_destinations': [
                {'query': r['query'], 'count': r['count']} for r in most_searched
            ],
        })
