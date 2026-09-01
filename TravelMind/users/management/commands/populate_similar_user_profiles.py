"""
Gives the existing "fake reviewer" accounts (created by
reviews/management/commands/populate_reviews.py to seed realistic review
content) complete, realistic travel-preference profiles, so the Similar
Users feature has real people to actually surface instead of the same 8
accounts sitting in the DB with every preference field blank.

Idempotent by design: a user is only touched if their profile is still
completely untouched (no travel type, season, activities, or budget set).
Once a profile has been populated - by this command or by the person
editing their own profile through the app - reruns skip that user
entirely, so this never overwrites real data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from destinations.models import Destination, TravelCategory, Season

User = get_user_model()

# Matches the accounts created by reviews/populate_reviews.py - reused
# rather than duplicated, since those are the "4-5(+) realistic users"
# that already exist for Similar Users to match against.
PROFILES = [
    {
        'username': 'elena_traveller',
        'gender': 'female',
        'short_summary': 'Cultural explorer who lives for old-town streets, local museums, and finding the best food market in every city.',
        'travel_type': 'cultural',
        'season': 'spring',
        'budget': '1200.00',
        'trip_duration_preference': 7,
        'activities': ['Art & Culture', 'Museums', 'Photography', 'Food & Dining'],
    },
    {
        'username': 'marko_mk',
        'gender': 'male',
        'short_summary': 'Beach-first traveller - give me warm water, good seafood, and a lively boardwalk in the evening.',
        'travel_type': 'beach',
        'season': 'summer',
        'budget': '900.00',
        'trip_duration_preference': 10,
        'activities': ['Beaches', 'Snorkeling', 'Nightlife', 'Food & Dining'],
    },
    {
        'username': 'sofia_explorer',
        'gender': 'female',
        'short_summary': 'Always chasing the next trail. Happiest with a backpack, a sunrise hike, and wildlife I have never seen before.',
        'travel_type': 'adventure',
        'season': 'summer',
        'budget': '1500.00',
        'trip_duration_preference': 12,
        'activities': ['Hiking', 'Wildlife Safari', 'Rock Climbing', 'Photography'],
    },
    {
        'username': 'alex_wanderer',
        'gender': 'male',
        'short_summary': 'City-break addict - architecture walks by day, rooftop bars by night, and a museum in between.',
        'travel_type': 'city',
        'season': 'autumn',
        'budget': '1100.00',
        'trip_duration_preference': 5,
        'activities': ['City Tours', 'Museums', 'Nightlife', 'Shopping'],
    },
    {
        'username': 'maja_journeys',
        'gender': 'female',
        'short_summary': 'Believes a trip should feel like a treat - good spas, better wine, and no rushing anywhere.',
        'travel_type': 'luxury',
        'season': 'winter',
        'budget': '4000.00',
        'trip_duration_preference': 8,
        'activities': ['Spa & Wellness', 'Wine Tasting', 'Shopping', 'Food & Dining'],
    },
    {
        'username': 'ivan_mk',
        'gender': 'male',
        'short_summary': 'Mountain person through and through - skis in winter, hiking boots the rest of the year.',
        'travel_type': 'mountain',
        'season': 'winter',
        'budget': '800.00',
        'trip_duration_preference': 6,
        'activities': ['Skiing', 'Hiking', 'Photography', 'Wildlife Safari'],
    },
    {
        'username': 'lena_world',
        'gender': 'female',
        'short_summary': 'Travels to slow down - beach loungers, spa afternoons, and zero itinerary.',
        'travel_type': 'relaxation',
        'season': 'summer',
        'budget': '2000.00',
        'trip_duration_preference': 9,
        'activities': ['Spa & Wellness', 'Beaches', 'Water Sports', 'Food & Dining'],
    },
    {
        'username': 'stefan_travels',
        'gender': 'male',
        'short_summary': 'Long trips, big trails. If it needs climbing gear or a full day of cycling, I am in.',
        'travel_type': 'adventure',
        'season': 'autumn',
        'budget': '1300.00',
        'trip_duration_preference': 14,
        'activities': ['Hiking', 'Rock Climbing', 'Cycling', 'Wildlife Safari'],
    },
]


class Command(BaseCommand):
    help = 'Populate realistic travel-preference profiles for the seeded reviewer accounts (idempotent).'

    def handle(self, *args, **options):
        updated, skipped, missing = 0, 0, []

        for profile in PROFILES:
            try:
                user = User.objects.get(username=profile['username'])
            except User.DoesNotExist:
                missing.append(profile['username'])
                continue

            already_populated = any([
                user.preferred_travel_type_id, user.preferred_season_id,
                user.preferred_activities, user.budget,
            ])
            if already_populated:
                skipped += 1
                continue

            category = TravelCategory.objects.filter(slug=profile['travel_type']).first()
            season = Season.objects.filter(slug=profile['season']).first()

            user.gender = profile['gender']
            user.short_summary = profile['short_summary']
            user.preferred_travel_type = category
            user.preferred_season = season
            user.budget = profile['budget']
            user.trip_duration_preference = profile['trip_duration_preference']
            user.preferred_activities = profile['activities']
            user.save()

            if category:
                favorites = Destination.objects.filter(travel_type=category).order_by('-popularity_score')[:3]
                user.favorite_destinations.add(*favorites)

            updated += 1

        self.stdout.write(self.style.SUCCESS(f'Done -- {updated} profile(s) populated, {skipped} already had data.'))
        if missing:
            self.stdout.write(self.style.WARNING(f'Not found (run populate_reviews first?): {", ".join(missing)}'))
