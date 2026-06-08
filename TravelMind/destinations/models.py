from django.db import models


class Destination(models.Model):
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

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
    ]

    REGION_CHOICES = [
        ('europe', 'Europe'),
        ('asia', 'Asia'),
        ('north_america', 'North America'),
        ('south_america', 'South America'),
        ('africa', 'Africa'),
        ('oceania', 'Australia & Oceania'),
    ]

    name = models.CharField(max_length=200)
    name_mk = models.CharField(max_length=200, blank=True, default='')
    city = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=100)
    description = models.TextField()
    description_mk = models.TextField(blank=True, default='')
    travel_type = models.CharField(max_length=20, choices=TRAVEL_TYPES)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    images = models.JSONField(default=list, blank=True)
    activities = models.JSONField(default=list, blank=True)
    attractions = models.TextField(blank=True)
    travel_tips = models.TextField(blank=True, default='')
    cost_breakdown = models.JSONField(default=dict, blank=True)
    best_season = models.CharField(max_length=20, choices=SEASON_CHOICES, blank=True)
    difficulty_level = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default='easy'
    )
    trip_duration_min = models.IntegerField(default=1)
    trip_duration_max = models.IntegerField(default=7)
    region = models.CharField(max_length=30, choices=REGION_CHOICES, blank=True)
    popularity_score = models.FloatField(default=0.0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-popularity_score', 'name']

    def __str__(self):
        return f"{self.name}, {self.country}"
