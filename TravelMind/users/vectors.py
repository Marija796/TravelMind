"""
User-to-user similarity for SimilarUsersView.

WHY A WEIGHTED PER-CRITERION SCORE, NOT A FLAT COSINE VECTOR
--------------------------------------------------------------
An earlier version concatenated every preference field into one numeric
vector (one-hot travel type, one-hot season, multi-hot activities, two
normalized scalars) and ran a single cosine similarity over it. That gives
each *dimension* equal weight, not each *criterion* - a person's activities
list alone occupies far more dimensions than travel_type or budget, so it
silently dominated the score with no way to reason about "how much does
travel type matter" independent of how many activity options happen to
exist. It also never looked at favorite_destinations at all.

This version scores each criterion independently (exact-match indicator for
travel_type/season, overlap coefficient for activities/favorite
destinations, bounded closeness for budget/duration - the same scoring
shapes already used for destination matching in recommendations/views.py,
for the same reasons) and combines them as an explicit weighted average.
Weights are named and inspectable instead of being an accident of
dimension counts.

A criterion is only included in the average when BOTH users being compared
have data for it - two users who simply haven't set a trip-duration
preference aren't "different" on that axis, they're incomparable on it, so
it drops out and the remaining weights are renormalized rather than
counting as a mismatch. If nothing is comparable between two users the
result is 0.0 - there is no basis to claim any similarity.

The output is always in [0, 1], purely a function of the two users' current
profile/favorites data - no randomness, no hardcoding, and no caching, so
it changes immediately when either user's preferences or favorites change.
"""
from core.similarity import overlap_coefficient

MAX_BUDGET_GAP_BASIS = 10000
MAX_DURATION_GAP_BASIS = 30

# Relative importance of each criterion - must sum to 1.0. Interests and
# favorite destinations carry the most weight since they reflect the widest
# range of a person's actual taste; travel type/season are coarser
# categorical signals; budget/duration matter but are the least distinctive
# (many unrelated travelers share a similar budget range by coincidence).
CRITERION_WEIGHTS = {
    'activities': 0.25,
    'favorite_destinations': 0.20,
    'travel_type': 0.20,
    'season': 0.15,
    'budget': 0.12,
    'duration': 0.08,
}
assert abs(sum(CRITERION_WEIGHTS.values()) - 1.0) < 1e-9


def _exact_match_criterion(a_id, b_id):
    if a_id is None or b_id is None:
        return None
    return 1.0 if a_id == b_id else 0.0


def _overlap_criterion(set_a, set_b):
    if not set_a or not set_b:
        return None
    return overlap_coefficient(set_a, set_b)


def _closeness_criterion(a_value, b_value, basis):
    if not a_value or not b_value:
        return None
    a_value, b_value = float(a_value), float(b_value)
    gap = abs(a_value - b_value) / max(a_value, b_value, basis * 0.01)
    return max(0.0, 1.0 - gap)


def calculate_similarity(user_a, user_b, favorites_a=None, favorites_b=None):
    """
    favorites_a/favorites_b: optional pre-fetched sets of favorite
    destination ids, so a caller comparing one user against many others
    (SimilarUsersView) can prefetch every candidate's favorites in one
    query instead of triggering one per comparison.
    """
    if favorites_a is None:
        favorites_a = set(user_a.favorite_destinations.values_list('id', flat=True))
    if favorites_b is None:
        favorites_b = set(user_b.favorite_destinations.values_list('id', flat=True))

    scores = {
        'travel_type': _exact_match_criterion(user_a.preferred_travel_type_id, user_b.preferred_travel_type_id),
        'season': _exact_match_criterion(user_a.preferred_season_id, user_b.preferred_season_id),
        'activities': _overlap_criterion(set(user_a.preferred_activities or []), set(user_b.preferred_activities or [])),
        'favorite_destinations': _overlap_criterion(favorites_a, favorites_b),
        'budget': _closeness_criterion(user_a.budget, user_b.budget, MAX_BUDGET_GAP_BASIS),
        'duration': _closeness_criterion(user_a.trip_duration_preference, user_b.trip_duration_preference, MAX_DURATION_GAP_BASIS),
    }

    comparable = {name: score for name, score in scores.items() if score is not None}
    if not comparable:
        return 0.0

    total_weight = sum(CRITERION_WEIGHTS[name] for name in comparable)
    return sum(CRITERION_WEIGHTS[name] * score for name, score in comparable.items()) / total_weight
