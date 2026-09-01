from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Administrator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    short_summary = models.CharField(max_length=280, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    preferred_travel_type = models.ForeignKey(
        'destinations.TravelCategory', on_delete=models.PROTECT,
        null=True, blank=True, related_name='+',
    )
    preferred_season = models.ForeignKey(
        'destinations.Season', on_delete=models.PROTECT,
        null=True, blank=True, related_name='+',
    )
    preferred_activities = models.JSONField(default=list, blank=True)
    trip_duration_preference = models.IntegerField(null=True, blank=True)
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
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
