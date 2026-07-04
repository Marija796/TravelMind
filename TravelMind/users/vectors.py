"""
Builds a fixed-order numeric preference vector for a user, used for cosine
similarity against other users (SimilarUsersView). Destination recommendation
matching (recommendations app) uses its own per-preference-group scoring
instead - see recommendations/views.py - since a flat concatenated vector
comparison doesn't suit every preference group equally well (e.g. a multi-hot
activities wishlist and a single-valued budget field need different
comparison semantics than a one-hot categorical choice).

Vector layout (31 dims):
  [0:7]   one-hot preferred_travel_type (CustomUser.TRAVEL_TYPES)
  [7:11]  one-hot preferred_season (CustomUser.SEASON_CHOICES)
  [11:29] multi-hot preferred_activities (core.constants.PREFERENCE_ACTIVITY_OPTIONS)
  [29]    normalized budget (0..1, ceiling MAX_BUDGET)
  [30]    normalized trip_duration_preference (0..1, ceiling MAX_DURATION_DAYS)
"""
from core.constants import PREFERENCE_ACTIVITY_OPTIONS
from .models import CustomUser

MAX_BUDGET = 10000
MAX_DURATION_DAYS = 30


def build_user_vector(user, max_budget=MAX_BUDGET, max_duration=MAX_DURATION_DAYS):
    vec = [1.0 if user.preferred_travel_type == t else 0.0 for t, _ in CustomUser.TRAVEL_TYPES]
    vec += [1.0 if user.preferred_season == s else 0.0 for s, _ in CustomUser.SEASON_CHOICES]
    user_activities = set(user.preferred_activities or [])
    vec += [1.0 if a in user_activities else 0.0 for a in PREFERENCE_ACTIVITY_OPTIONS]
    vec.append(min(float(user.budget or 0) / max_budget, 1.0))
    vec.append(min(float(user.trip_duration_preference or 0) / max_duration, 1.0))
    return vec
