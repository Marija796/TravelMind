"""
Cross-app shared constants. Mirrors frontend/src/types/destination.ts's
ACTIVITY_OPTIONS by hand - there is no shared source of truth across the
Python/TS boundary, matching the existing precedent of TRAVEL_TYPES/
SEASON_CHOICES already being duplicated between users/models.py and
destinations/models.py. A fixed list (not computed dynamically from
observed data) keeps preference-vector dimensionality stable over time.
"""

PREFERENCE_ACTIVITY_OPTIONS = [
    'Hiking', 'Beaches', 'Nightlife', 'Museums', 'Food & Dining',
    'Skiing', 'Surfing', 'Snorkeling', 'Rock Climbing', 'Cycling',
    'Shopping', 'Art & Culture', 'Photography', 'Wildlife Safari',
    'Spa & Wellness', 'Water Sports', 'City Tours', 'Wine Tasting',
]
