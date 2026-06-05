from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    favorite_destination_ids = serializers.SerializerMethodField()
    wishlist_destination_ids = serializers.SerializerMethodField()
    visited_destination_ids = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'bio',
            'preferred_travel_type',
            'preferred_season',
            'preferred_activities',
            'trip_duration_preference',
            'budget',
            'avatar_url',
            'favorite_destination_ids',
            'wishlist_destination_ids',
            'visited_destination_ids',
        ]

    def get_favorite_destination_ids(self, obj):
        return list(obj.favorite_destinations.values_list('id', flat=True))

    def get_wishlist_destination_ids(self, obj):
        return list(obj.wishlist_destinations.values_list('id', flat=True))

    def get_visited_destination_ids(self, obj):
        return list(obj.visited_destinations.values_list('id', flat=True))


class GoogleAuthSerializer(serializers.Serializer):
    credential = serializers.CharField(required=False)
    code = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get('credential') and not attrs.get('code'):
            raise serializers.ValidationError('Either credential or code is required.')
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        return attrs