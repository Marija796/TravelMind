from django.db import models
from .link_generators import generate_booking_url, generate_flight_url


class TravelCategory(models.Model):
    """
    DB-managed replacement for the old hardcoded travel-type choices, so an
    administrator can add/rename/retire categories at runtime instead of
    requiring a code change. name/name_mk mirror Destination's existing
    bilingual-field convention (rather than relying solely on the frontend's
    static i18n dictionary) because a category an admin adds later has no
    pre-existing translation key - the DB row must carry both names itself.
    slug is the stable identifier referenced by scoring code and URLs/query
    params, seeded to match the original choice keys exactly.
    """
    slug = models.SlugField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    name_mk = models.CharField(max_length=100, blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Travel categories'

    def __str__(self):
        return self.name


class Season(models.Model):
    """DB-managed replacement for the old hardcoded season choices - see TravelCategory docstring."""
    slug = models.SlugField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    name_mk = models.CharField(max_length=50, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Destination(models.Model):
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
    country_mk = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    description_mk = models.TextField(blank=True, default='')
    travel_type = models.ForeignKey(
        TravelCategory, on_delete=models.PROTECT, related_name='destinations',
    )
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    images = models.JSONField(default=list, blank=True)
    activities = models.JSONField(default=list, blank=True)
    attractions = models.TextField(blank=True)
    travel_tips = models.TextField(blank=True, default='')
    cost_breakdown = models.JSONField(default=dict, blank=True)
    best_season = models.ForeignKey(
        Season, on_delete=models.PROTECT, related_name='destinations',
        null=True, blank=True,
    )
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
    booking_url = models.URLField(blank=True, default='')
    flight_url = models.URLField(blank=True, default='')

    class Meta:
        ordering = ['-popularity_score', 'name']

    def __str__(self):
        return f"{self.name}, {self.country}"

    def save(self, *args, **kwargs):
        # A blank booking_url/flight_url always gets a real, destination-
        # specific default (not a generic homepage) so every destination -
        # seeded or admin-created - has a working link with zero required
        # admin data-entry. An admin can still override either field with a
        # specific URL; clearing it back to blank and saving again just
        # regenerates the default.
        if not self.booking_url:
            self.booking_url = generate_booking_url(self.city, self.country)
        if not self.flight_url:
            self.flight_url = generate_flight_url(self.city, self.name)
        super().save(*args, **kwargs)


class SearchLog(models.Model):
    """One row per non-empty destination search - powers the admin
    dashboard's real 'most searched destinations' stat (see
    DestinationListView.list() in views.py, which writes these)."""
    query = models.CharField(max_length=200)
    results_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
