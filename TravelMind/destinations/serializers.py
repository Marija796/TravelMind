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
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(pk=request.user.pk).exists()
        return False

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.wishlisted_by.filter(pk=request.user.pk).exists()
        return False

    def get_is_visited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.visited_by.filter(pk=request.user.pk).exists()
        return False
