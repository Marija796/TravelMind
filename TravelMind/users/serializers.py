from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from destinations.models import TravelCategory, Season
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']

    def validate_email(self, value):
        # email isn't a unique DB column (a handful of pre-existing accounts
        # already share one, predating email-based login) - guard against
        # new registrations adding to that, since EmailOrUsernameBackend
        # can only log in by email when it's unique.
        if value and CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

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
    # Explicit SlugRelatedField (same reasoning as DestinationSerializer):
    # preferred_travel_type/preferred_season are now FKs to the dynamic
    # TravelCategory/Season tables, but the frontend expects the same
    # "preferred_travel_type": "beach" string shape it always got.
    preferred_travel_type = serializers.SlugRelatedField(
        slug_field='slug', queryset=TravelCategory.objects.all(), required=False, allow_null=True,
    )
    preferred_season = serializers.SlugRelatedField(
        slug_field='slug', queryset=Season.objects.all(), required=False, allow_null=True,
    )

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'role',
            'short_summary',
            'gender',
            'preferred_travel_type',
            'preferred_season',
            'preferred_activities',
            'trip_duration_preference',
            'budget',
            'profile_image',
            'favorite_destination_ids',
            'wishlist_destination_ids',
            'visited_destination_ids',
        ]
        # role must never be settable through the public profile endpoint -
        # ProfileView.put/patch passes request.data straight into this
        # serializer with partial=True, so without this a user could
        # self-promote via PATCH /api/users/profile/ {"role": "admin"}.
        read_only_fields = ['role']

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