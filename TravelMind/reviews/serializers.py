from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.CharField(source='user.avatar_url', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'username',
            'avatar_url',
            'destination',
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = ['user', 'destination']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
