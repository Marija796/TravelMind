"""
Admin-only user management endpoints. Kept separate from the public
views.py/serializers.py so the admin-only surface (every view here gated by
IsAdminRole) is easy to audit at a glance.
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from core.permissions import IsAdminRole
from .models import CustomUser
from .admin_serializers import AdminUserSerializer, AdminUserCreateSerializer, AdminTokenObtainPairSerializer
from .views import _compute_similar_users


class AdminTokenObtainPairView(TokenObtainPairView):
    """The separate Administrator Login page's backend - see
    AdminTokenObtainPairSerializer for why a non-admin account is rejected
    here even with a correct password."""
    serializer_class = AdminTokenObtainPairSerializer


class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminUserSerializer
    # select_related: AdminUserSerializer's SlugRelatedField reads
    # preferred_travel_type.slug/preferred_season.slug, which would
    # otherwise issue one extra query per FK per row (measured: 21 queries
    # for a 17-row list without this).
    queryset = CustomUser.objects.select_related(
        'preferred_travel_type', 'preferred_season',
    ).order_by('-date_joined')
    search_fields = ['username', 'email']
    filterset_fields = ['role', 'is_active']
    ordering_fields = ['date_joined', 'username', 'last_login']


class AdminUserCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminUserCreateSerializer
    queryset = CustomUser.objects.all()


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminUserSerializer
    queryset = CustomUser.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.pk == request.user.pk:
            return Response(
                {'error': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class AdminSimilarUsersView(APIView):
    """
    Lets an admin inspect any user's computed Similar Users results, using
    the exact same _compute_similar_users function that also backs the
    contextual "people with similar interests" section on a destination's
    detail page (see DestinationInterestedUsersView) - not a separate/fake
    calculation - so an admin can verify the percentages shown anywhere in
    the app are real and reproduce them for a specific account. Always live
    (no cache to invalidate) - re-fetching this endpoint after editing a
    user's preferences via the admin panel already reflects the change.
    """
    permission_classes = [IsAdminRole]

    def get(self, request, pk):
        target = get_object_or_404(CustomUser, pk=pk)
        data = _compute_similar_users(request, target)
        data['target'] = {
            'id': target.id,
            'username': target.username,
            'preferred_travel_type': target.preferred_travel_type.slug if target.preferred_travel_type_id else None,
            'preferred_season': target.preferred_season.slug if target.preferred_season_id else None,
            'preferred_activities': target.preferred_activities,
            'budget': str(target.budget) if target.budget else None,
            'trip_duration_preference': target.trip_duration_preference,
        }
        return Response(data)
