from rest_framework import serializers
from .models import Review, AppReview


def _build_profile_image_url(user, context):
    request = context.get('request')
    if user.profile_image and request:
        return request.build_absolute_uri(user.profile_image.url)
    return None


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id',
            'username',
            'profile_image',
            'destination',
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = ['user', 'destination']

    def get_profile_image(self, obj):
        return _build_profile_image_url(obj.user, self.context)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AppReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = AppReview
        fields = ['id', 'username', 'profile_image', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'username', 'profile_image', 'created_at', 'updated_at']

    def get_profile_image(self, obj):
        return _build_profile_image_url(obj.user, self.context)

    def validate(self, attrs):
        # Defense in depth alongside the DB-level OneToOneField: without this,
        # a duplicate create would surface as an opaque IntegrityError/500
        # instead of a clean 400 with a helpful message.
        request = self.context.get('request')
        if request and self.instance is None and AppReview.objects.filter(user=request.user).exists():
            raise serializers.ValidationError(
                'You have already submitted a review. Please edit your existing review instead.'
            )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
