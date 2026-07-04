from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'preferred_travel_type', 'preferred_season', 'budget']
    list_filter = ['preferred_travel_type', 'preferred_season']
    search_fields = ['username', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('Travel Preferences', {
            'fields': ('short_summary', 'gender', 'preferred_travel_type', 'preferred_season',
                       'preferred_activities', 'trip_duration_preference', 'budget',
                       'profile_image', 'favorite_destinations'),
        }),
    )
