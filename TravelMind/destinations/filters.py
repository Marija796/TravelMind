import django_filters
from .models import Destination


class DestinationFilter(django_filters.FilterSet):
    travel_type = django_filters.ChoiceFilter(choices=Destination.TRAVEL_TYPES)
    difficulty_level = django_filters.ChoiceFilter(choices=Destination.DIFFICULTY_CHOICES)
    budget_max = django_filters.NumberFilter(field_name='estimated_cost', lookup_expr='lte')
    budget_min = django_filters.NumberFilter(field_name='estimated_cost', lookup_expr='gte')
    season = django_filters.ChoiceFilter(field_name='best_season', choices=Destination.SEASON_CHOICES)
    duration_max = django_filters.NumberFilter(field_name='trip_duration_max', lookup_expr='lte')
    duration_min = django_filters.NumberFilter(field_name='trip_duration_min', lookup_expr='gte')
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    region = django_filters.ChoiceFilter(choices=Destination.REGION_CHOICES)

    class Meta:
        model = Destination
        fields = []
