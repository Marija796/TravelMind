from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    TRAVEL_TYPES = [
        ('beach', 'Beach'),
        ('mountain', 'Mountain'),
        ('city', 'City Tourism'),
        ('adventure', 'Adventure'),
        ('cultural', 'Cultural'),
        ('luxury', 'Luxury'),
        ('relaxation', 'Relaxation'),
    ]

    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    ]

    bio = models.TextField(blank=True)
    preferred_travel_type = models.CharField(
        max_length=20, choices=TRAVEL_TYPES, blank=True
    )
    preferred_season = models.CharField(
        max_length=20, choices=SEASON_CHOICES, blank=True
    )
    preferred_activities = models.JSONField(default=list, blank=True)
    trip_duration_preference = models.IntegerField(null=True, blank=True)
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    avatar_url = models.URLField(blank=True, null=True)
    favorite_destinations = models.ManyToManyField(
        'destinations.Destination',
        blank=True,
        related_name='favorited_by'
    )
    wishlist_destinations = models.ManyToManyField(
        'destinations.Destination',
        blank=True,
        related_name='wishlisted_by'
    )
    visited_destinations = models.ManyToManyField(
        'destinations.Destination',
        blank=True,
        related_name='visited_by'
    )

    def __str__(self):
        return self.username
