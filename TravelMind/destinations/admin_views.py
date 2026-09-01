"""Admin-only CRUD for the dynamic travel-type/season taxonomy."""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import ProtectedError
from core.permissions import IsAdminRole
from .models import TravelCategory, Season
from .taxonomy_serializers import TravelCategorySerializer, SeasonSerializer


class _ProtectedDeleteMixin:
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except ProtectedError as e:
            count = len(e.protected_objects)
            return Response(
                {'error': f'Cannot delete "{instance.name}": still in use by {count} record(s).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TravelCategoryListView(generics.ListAPIView):
    # Every consumer of this list (FilterPanel, Profile, Recommendations,
    # the admin destination form) sits behind a login-gated page - there is
    # no anonymous/guest path left in the app, so this requires auth too
    # rather than being AllowAny. Tiny, fixed-size table - no pagination.
    permission_classes = [IsAuthenticated]
    pagination_class = None
    queryset = TravelCategory.objects.all()
    serializer_class = TravelCategorySerializer


class SeasonListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


class AdminTravelCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    pagination_class = None
    queryset = TravelCategory.objects.all()
    serializer_class = TravelCategorySerializer


class AdminTravelCategoryDetailView(_ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = TravelCategory.objects.all()
    serializer_class = TravelCategorySerializer


class AdminSeasonListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    pagination_class = None
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


class AdminSeasonDetailView(_ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
