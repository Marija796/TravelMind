from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from destinations.models import TravelCategory, Season
from .models import CustomUser


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Backs the separate /api/users/admin/login/ endpoint - real backend
    authorization for the dedicated Administrator Login page, not a
    frontend-only check. Reuses the exact same authenticate() call (and
    therefore the same EmailOrUsernameBackend, so admins can still log in
    with either username or email) as the regular login endpoint, then
    additionally requires role == 'admin'.

    Raises the identical generic error TokenObtainSerializer already uses
    for a wrong password, rather than a distinct "not an admin" message -
    this endpoint must never reveal whether a rejected login had valid
    credentials for a non-admin account or simply the wrong password.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role != 'admin':
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )
        return data


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Superset of the public UserSerializer for admin user management - unlike
    UserSerializer, role/is_active are writable here (this view is already
    gated by IsAdminRole, so there's no self-promotion risk to guard against
    the way there is on the public profile endpoint).
    """
    # Same SlugRelatedField treatment as the public UserSerializer, so this
    # endpoint returns/accepts "beach" rather than a raw FK id.
    preferred_travel_type = serializers.SlugRelatedField(
        slug_field='slug', queryset=TravelCategory.objects.all(), required=False, allow_null=True,
    )
    preferred_season = serializers.SlugRelatedField(
        slug_field='slug', queryset=Season.objects.all(), required=False, allow_null=True,
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'role', 'is_active',
            'short_summary', 'gender', 'preferred_travel_type', 'preferred_season',
            'preferred_activities', 'trip_duration_preference', 'budget',
            'date_joined', 'last_login',
        ]
        read_only_fields = ['date_joined', 'last_login']


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    # Optional at creation - lets an admin create a fully-profiled realistic
    # user (travel type/season/budget/activities) in one step, e.g. to add
    # another account for the Similar Users pool, without a separate edit
    # step. Same SlugRelatedField treatment as AdminUserSerializer.
    preferred_travel_type = serializers.SlugRelatedField(
        slug_field='slug', queryset=TravelCategory.objects.all(), required=False, allow_null=True,
    )
    preferred_season = serializers.SlugRelatedField(
        slug_field='slug', queryset=Season.objects.all(), required=False, allow_null=True,
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'role', 'is_active',
            'short_summary', 'gender', 'preferred_travel_type', 'preferred_season',
            'preferred_activities', 'trip_duration_preference', 'budget',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
