from rest_framework import serializers
from .models import Destination


class DestinationSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    is_visited = serializers.SerializerMethodField()

    class Meta:
        model = Destination
        fields = [
            'id',
            'slug',
            'name',
            'name_mk',
            'city',
            'country',
            'region',
            'description',
            'description_mk',
            'travel_type',
            'estimated_cost',
            'image_url',
            'images',
            'activities',
            'attractions',
            'travel_tips',
            'cost_breakdown',
            'best_season',
            'difficulty_level',
            'trip_duration_min',
            'trip_duration_max',
            'popularity_score',
            'latitude',
            'longitude',
            'average_rating',
            'review_count',
            'is_favorited',
            'is_wishlisted',
            'is_visited',
            'created_at',
        ]

    def get_average_rating(self, obj):
        # Fast path: callers that already annotated the queryset (e.g. the
        # recommendations views) avoid a per-object query here.
        annotated = getattr(obj, 'avg_rating_annotated', None)
        if annotated is not None:
            return round(annotated, 1)
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

    def get_review_count(self, obj):
        annotated = getattr(obj, 'review_count_annotated', None)
        if annotated is not None:
            return annotated
        return obj.reviews.count()

    def get_is_favorited(self, obj):
        favorited_ids = self.context.get('favorited_ids')
        if favorited_ids is not None:
            return obj.pk in favorited_ids
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(pk=request.user.pk).exists()
        return False

    def get_is_wishlisted(self, obj):
        wishlisted_ids = self.context.get('wishlisted_ids')
        if wishlisted_ids is not None:
            return obj.pk in wishlisted_ids
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.wishlisted_by.filter(pk=request.user.pk).exists()
        return False

    def get_is_visited(self, obj):
        visited_ids = self.context.get('visited_ids')
        if visited_ids is not None:
            return obj.pk in visited_ids
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.visited_by.filter(pk=request.user.pk).exists()
        return False
