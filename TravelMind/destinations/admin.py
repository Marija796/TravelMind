from django.contrib import admin
from .models import Destination, TravelCategory, Season


@admin.register(TravelCategory)
class TravelCategoryAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'name_mk', 'order']
    search_fields = ['slug', 'name', 'name_mk']


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'name_mk', 'order']
    search_fields = ['slug', 'name', 'name_mk']


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'travel_type', 'estimated_cost', 'best_season', 'difficulty_level', 'popularity_score']
    list_filter = ['travel_type', 'best_season', 'difficulty_level']
    search_fields = ['name', 'country', 'description']
    list_editable = ['popularity_score']
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'country', 'description', 'travel_type')}),
        ('Media', {'fields': ('image_url', 'images')}),
        ('Details', {'fields': ('estimated_cost', 'best_season', 'difficulty_level', 'trip_duration_min', 'trip_duration_max')}),
        ('Activities & Attractions', {'fields': ('activities', 'attractions')}),
        ('Metadata', {'fields': ('popularity_score', 'latitude', 'longitude')}),
    )
