from rest_framework import serializers
from .models import RecommendationHistory


class RecommendationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationHistory
        fields = ['id', 'preferences_snapshot', 'results_snapshot', 'result_count', 'created_at']
