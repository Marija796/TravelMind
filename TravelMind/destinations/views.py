from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count
from django.utils.text import slugify
from core.permissions import IsAdminRole
from .models import Destination, SearchLog
from .serializers import DestinationSerializer
from .filters import DestinationFilter


def _annotated_destination_queryset():
    # select_related joins travel_type/best_season so DestinationSerializer's
    # SlugRelatedField output (travel_type.slug, best_season.slug) doesn't
    # trigger one extra query per row; the Avg/Count annotations give
    # get_average_rating/get_review_count their O(1) fast path instead of
    # each running its own obj.reviews.all()/.count() per row. Without
    # these, a single 12-item page of destinations was measured at ~99
    # queries instead of the handful this produces.
    return Destination.objects.select_related('travel_type', 'best_season').annotate(
        avg_rating_annotated=Avg('reviews__rating'),
        review_count_annotated=Count('reviews', distinct=True),
    )


class DestinationListView(generics.ListAPIView):
    queryset = _annotated_destination_queryset()
    serializer_class = DestinationSerializer
    # Destination browsing requires an account (see IsAuthenticated below on
    # every view in this module) - there is no anonymous/guest access path
    # anywhere in the app.
    permission_classes = [IsAuthenticated]
    filterset_class = DestinationFilter
    search_fields = ['name', 'name_mk', 'city', 'country', 'country_mk', 'description', 'description_mk']
    ordering_fields = ['popularity_score', 'estimated_cost', 'name', 'created_at']
    ordering = ['-popularity_score']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        user = self.request.user
        if user.is_authenticated:
            # Pre-fetched once for the whole page (3 queries total) instead
            # of DestinationSerializer's per-object fallback
            # (obj.favorited_by.filter(...).exists(), etc.), which would
            # otherwise add 3 more queries per destination on the page.
            context['favorited_ids'] = set(user.favorite_destinations.values_list('id', flat=True))
            context['wishlisted_ids'] = set(user.wishlist_destinations.values_list('id', flat=True))
            context['visited_ids'] = set(user.visited_destinations.values_list('id', flat=True))
        return context

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        query = request.query_params.get('search', '').strip()
        if query:
            try:
                # count is on the paginated response, not len(response.data)
                # (which would be one page's worth) - powers the admin
                # dashboard's real "most searched destinations" stat.
                results_count = response.data.get('count', 0) if hasattr(response.data, 'get') else 0
                SearchLog.objects.create(query=query, results_count=results_count)
            except Exception:
                # A logging failure must never break the actual search
                # response the user is waiting on.
                pass
        return response


class DestinationDetailView(generics.RetrieveAPIView):
    queryset = _annotated_destination_queryset()
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class DestinationDetailBySlugView(generics.RetrieveAPIView):
    queryset = _annotated_destination_queryset()
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class AdminDestinationCreateView(generics.CreateAPIView):
    # Separate admin-only view class (rather than mixing IsAdminRole into
    # the public AllowAny list/detail views above) so GET stays public and
    # unauthenticated while create/update/delete stay admin-gated.
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminRole]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        # slug is unique+blank=True on the model with no auto-population -
        # existing rows got theirs from the seeding management command, but
        # an admin filling out the create form has no reason to hand-craft
        # a slug, so derive and de-duplicate one from the name when omitted.
        slug = serializer.validated_data.get('slug') or slugify(serializer.validated_data['name'])
        base_slug = slug
        n = 2
        while Destination.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{n}"
            n += 1
        serializer.save(slug=slug)


class AdminDestinationUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminRole]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
