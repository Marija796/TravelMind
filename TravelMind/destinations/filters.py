import django_filters
from django.db.models import Q
from .models import Destination, TravelCategory, Season


class DestinationFilter(django_filters.FilterSet):
    # ModelChoiceFilter + to_field_name='slug' so ?travel_type=beach in the
    # URL keeps working unchanged now that travel_type/best_season are FKs
    # to the dynamically-managed TravelCategory/Season tables instead of
    # static choices - no frontend query-param change needed.
    travel_type = django_filters.ModelChoiceFilter(
        queryset=TravelCategory.objects.all(), to_field_name='slug',
    )
    difficulty_level = django_filters.ChoiceFilter(choices=Destination.DIFFICULTY_CHOICES)
    budget_max = django_filters.NumberFilter(field_name='estimated_cost', lookup_expr='lte')
    budget_min = django_filters.NumberFilter(field_name='estimated_cost', lookup_expr='gte')
    season = django_filters.ModelChoiceFilter(
        field_name='best_season', queryset=Season.objects.all(), to_field_name='slug',
    )
    duration_max = django_filters.NumberFilter(field_name='trip_duration_max', lookup_expr='lte')
    duration_min = django_filters.NumberFilter(field_name='trip_duration_min', lookup_expr='gte')
    # Checks both country and country_mk so the dedicated country filter
    # (FilterPanel's "Country" box, distinct from the general search bar)
    # matches a Macedonian query like "Герман" the same way English does.
    country = django_filters.CharFilter(method='filter_country')
    region = django_filters.ChoiceFilter(choices=Destination.REGION_CHOICES)

    def filter_country(self, queryset, name, value):
        return queryset.filter(Q(country__icontains=value) | Q(country_mk__icontains=value))

    class Meta:
        model = Destination
        fields = []
