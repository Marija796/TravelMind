from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from .models import Destination
from .serializers import DestinationSerializer
from .filters import DestinationFilter
from users.authentication import SilentJWTAuthentication


class DestinationListView(generics.ListAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SilentJWTAuthentication]
    filterset_class = DestinationFilter
    search_fields = ['name', 'name_mk', 'city', 'country', 'description', 'description_mk']
    ordering_fields = ['popularity_score', 'estimated_cost', 'name', 'created_at']
    ordering = ['-popularity_score']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class DestinationDetailView(generics.RetrieveAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SilentJWTAuthentication]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class DestinationDetailBySlugView(generics.RetrieveAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SilentJWTAuthentication]
    lookup_field = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
