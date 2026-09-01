"""
Destination recommendation scoring.

WHY NOT PLAIN COSINE SIMILARITY OVER ONE CONCATENATED VECTOR
--------------------------------------------------------------
Earlier iterations of this module concatenated every preference field
(travel_type, season, activities, budget, duration) into a single numeric
vector and took one cosine similarity against a matching destination vector.
That approach has three structural problems that no amount of dimension
weighting can fully fix:

  1. It applies the same "angle between vectors" math to fields with
     completely different semantics: an exact-match categorical choice
     (travel_type), a multi-select wishlist that should reward *coverage*
     regardless of its size (activities), and continuous numeric fields
     where what matters is *distance*, not direction (budget, duration).
     Cosine similarity of a single isolated positive scalar is degenerate
     (always exactly 1.0), and cosine similarity of a wishlist vector
     penalizes users for selecting many activities even when a destination
     satisfies all of them.
  2. It has no way to express *confidence*. A user who has only ever set
     one preference field and a user with a fully fleshed-out profile both
     get scored on the same 0-1 scale with no accounting for how little
     was actually being compared - so a single lucky match can produce a
     100% score from almost no information. That is precisely the
     "unrealistic 100% match" problem this rewrite fixes.
  3. It has no natural ceiling below 1.0. Real recommendation systems
     (and users) don't trust a literal "100% match" - there's always some
     uncertainty - but raw similarity math has no concept of that; it will
     happily report 1.0 whenever the available signals align.

THE APPROACH USED HERE: a hybrid rule-based weighted scoring model
--------------------------------------------------------------
Each preference is its own named "criterion" (see CRITERIA below) with a
scoring function suited to its actual semantics:
  - travel_type / season: exact-match indicator (cosine similarity of a
    one-hot pair reduces to this, but it's simpler to read as what it is).
  - activities: an overlap coefficient (core.similarity.overlap_coefficient)
    - the fraction of a destination's activities that the user's wishlist
      covers - rather than cosine similarity, so a broad wishlist isn't
      penalized for its size.
  - budget / duration: a bounded closeness measure (1 - normalized
    distance), since these are continuous quantities where nearness matters,
    not direction.

Per-criterion scores are combined as a WEIGHTED GEOMETRIC MEAN (each score
raised to its normalized weight, then multiplied together) rather than a
weighted arithmetic mean, because multiplying means any one badly-conflicting
criterion (e.g. completely wrong travel_type) collapses the whole score
instead of being diluted by everything else - conflicts get penalized, not
averaged away.

Two further adjustments make the output realistic rather than just "well
combined":
  - A CONFIDENCE factor scales the raw score down based on how much of the
    user's profile was actually available to compare (see
    _confidence_factor). A match based on one or two stated preferences is
    capped lower than a match based on a fully-specified profile, even if
    both are "perfect" on the criteria that were available - mirroring how
    a real recommendation should be less confident with less information.
  - A hard MAX_MATCH_SCORE ceiling below 1.0 guarantees no destination is
    ever reported as a literal 100% match.

This produces the score distribution real users expect: only a handful of
destinations that align on nearly everything reach the 90s, a good-but-
imperfect match lands in the 70s-80s, a loosely-aligned one in the 50s-60s,
and destinations that conflict on important criteria are filtered out
entirely (see SIMILARITY_THRESHOLD) rather than surfaced with a padded
score.

MODULARITY
--------------------------------------------------------------
Adding a new preference signal later (e.g. a future "climate" or "travel
style" field) means adding one Criterion entry and one small scoring
function - the combination/confidence/cap machinery below is generic and
doesn't need to change.
"""
import math
from dataclasses import dataclass
from typing import Callable

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count

from core.similarity import overlap_coefficient
from destinations.models import Destination
from destinations.serializers import DestinationSerializer
from .models import RecommendationHistory
from .serializers import RecommendationHistorySerializer

# --- Realism controls -------------------------------------------------
# Below this, a destination conflicts too much (or shares too little
# signal) with the user's stated preferences to be worth showing at all.
SIMILARITY_THRESHOLD = 0.45

# No destination is ever reported as a literal 100% match - there is
# always some irreducible uncertainty in a preference-based recommendation.
MAX_MATCH_SCORE = 0.97

# Floor applied when the user has stated only a small fraction of the
# possible preference criteria - see _confidence_factor. Even a "perfect"
# match on one criterion shouldn't be reported with the same confidence as
# a perfect match across a fully-specified profile.
MIN_CONFIDENCE = 0.55


@dataclass(frozen=True)
class Criterion:
    name: str
    weight: float
    is_active: Callable[[object], bool]
    score: Callable[[object, Destination], float]


def _type_active(prefs):
    return bool(getattr(prefs, 'preferred_travel_type_id', None))


def _type_score(prefs, destination):
    # travel_type/preferred_travel_type are now FKs into the admin-managed
    # TravelCategory table rather than a fixed static-choice list. Comparing
    # by id (the *_id shadow attribute Django provides for every FK, which
    # reads the raw column with no extra query) is exactly equivalent to the
    # old one-hot cosine_similarity comparison - for one-hot vectors with a
    # single 1, cosine similarity is 1.0 iff the same category is set and
    # 0.0 otherwise - but avoids fetching the category list at all, so this
    # can run inside the per-destination scoring loop with zero extra
    # queries instead of re-querying the lookup table on every call.
    return 1.0 if prefs.preferred_travel_type_id == destination.travel_type_id else 0.0


def _season_active(prefs):
    return bool(getattr(prefs, 'preferred_season_id', None))


def _season_score(prefs, destination):
    return 1.0 if prefs.preferred_season_id == destination.best_season_id else 0.0


def _activities_active(prefs):
    return bool(prefs.preferred_activities)


def _activities_score(prefs, destination):
    return overlap_coefficient(set(prefs.preferred_activities), set(destination.activities or []))


def _budget_active(prefs):
    return bool(prefs.budget)


def _budget_score(prefs, destination):
    """
    Budget is a ceiling, not a target: a destination costing at or under the
    user's stated budget is a perfect fit regardless of how far under it is
    (nobody complains that a trip was too cheap). Going over budget is
    penalized proportionally to how far over, as a fraction of the budget
    itself - a destination 30% over budget is a mild stretch, one costing
    3x the budget is not a real option. Using a fixed normalization ceiling
    here (as earlier versions did) hid genuine mismatches whenever both
    figures were small relative to that ceiling (e.g. a $50 budget against
    a $650 destination looked "close" only because both are far below a
    $10,000 ceiling) - the relative comparison below doesn't have that blind
    spot.
    """
    budget = float(prefs.budget)
    cost = float(destination.estimated_cost or 0)
    if cost <= budget:
        return 1.0
    overage_ratio = (cost - budget) / budget
    return max(0.0, 1.0 - overage_ratio)


def _duration_active(prefs):
    return bool(getattr(prefs, 'trip_duration_preference', None))


def _duration_score(prefs, destination):
    """
    Duration is a target, not a ceiling (unlike budget), so distance in
    either direction matters - but the distance is measured relative to the
    trip length itself, not a fixed day-count ceiling: a 3-day gap matters a
    lot for someone planning a 5-day trip, and much less for someone
    planning a 20-day one.
    """
    user_days = float(prefs.trip_duration_preference)
    dest_days = (destination.trip_duration_min + destination.trip_duration_max) / 2
    largest = max(user_days, dest_days, 1.0)
    return max(0.0, 1.0 - abs(user_days - dest_days) / largest)


# Relative importance of each criterion (destination type and budget matter
# most; secondary preferences matter less) - also used as the geometric
# mean's normalized exponents and as the basis for the confidence factor.
CRITERIA = [
    Criterion('type', 3.0, _type_active, _type_score),
    Criterion('budget', 2.5, _budget_active, _budget_score),
    Criterion('season', 2.0, _season_active, _season_score),
    Criterion('activities', 2.0, _activities_active, _activities_score),
    Criterion('duration', 1.0, _duration_active, _duration_score),
]

TOTAL_CRITERIA_WEIGHT = sum(c.weight for c in CRITERIA)


def _confidence_factor(active_criteria):
    """
    Scales the raw score down when only a small fraction of the possible
    preference criteria were available to compare. Ranges from
    MIN_CONFIDENCE (almost nothing stated) to 1.0 (every criterion active),
    scaled linearly by how much of the total possible weight is active -
    this is what stops a one-field profile from producing a padded,
    over-confident 100% match.
    """
    active_weight = sum(c.weight for c in active_criteria)
    coverage = active_weight / TOTAL_CRITERIA_WEIGHT
    return MIN_CONFIDENCE + (1 - MIN_CONFIDENCE) * coverage


def score_destination(destination, user):
    """Returns (realistic match score in [0, MAX_MATCH_SCORE], human-readable breakdown dict)."""
    active = [c for c in CRITERIA if c.is_active(user)]
    if not active:
        return 0.0, _dimension_breakdown(destination, user)

    active_weight = sum(c.weight for c in active)
    raw_score = math.prod(
        c.score(user, destination) ** (c.weight / active_weight) for c in active
    )
    confidence = _confidence_factor(active)
    similarity = min(raw_score * confidence, MAX_MATCH_SCORE)

    breakdown = _dimension_breakdown(destination, user)
    return similarity, breakdown


# Human-readable labels surfaced alongside the numeric score/percentage,
# matching the realistic score bands described above. Ordered highest-first;
# the first threshold the score clears wins.
MATCH_QUALITY_BANDS = [
    (0.90, 'Excellent Match'),
    (0.75, 'Great Match'),
    (0.50, 'Good Match'),
]


def match_quality_label(score):
    for threshold, label in MATCH_QUALITY_BANDS:
        if score >= threshold:
            return label
    return 'Fair Match'


def _dimension_breakdown(destination, user):
    # Recomputed directly from the raw fields (independent of the scoring
    # math) purely to drive the human-readable match explanation below -
    # this keeps generate_explanation() and the frontend's ScoreBreakdown
    # shape completely unchanged from the original additive-scoring design.
    return {
        'type_match': 40 if user.preferred_travel_type_id and destination.travel_type_id == user.preferred_travel_type_id else 0,
        'budget_fit': 30 if user.budget and destination.estimated_cost <= user.budget else 0,
        'season_match': 20 if user.preferred_season_id and destination.best_season_id == user.preferred_season_id else 0,
        'activity_overlap': min(
            len(set(user.preferred_activities or []) & set(destination.activities or [])) * 10, 30
        ),
    }


def generate_explanation(destination, user, breakdown):
    reasons = []

    if breakdown['type_match'] > 0:
        # destination.travel_type is select_related in _annotated_destinations(),
        # so this reads the already-joined TravelCategory - no extra query.
        reasons.append(f"it matches your {destination.travel_type.name.lower()} travel style")

    if breakdown['budget_fit'] > 0 and user.budget:
        reasons.append(f"fits your ${int(user.budget):,} budget at ${int(destination.estimated_cost):,}")

    if breakdown['season_match'] > 0 and destination.best_season:
        reasons.append(f"is best visited in {destination.best_season.name.lower()} (your preferred season)")

    if breakdown['activity_overlap'] > 0 and user.preferred_activities and destination.activities:
        matching = sorted(set(user.preferred_activities) & set(destination.activities))
        if len(matching) == 1:
            reasons.append(f"offers {matching[0]} from your interests")
        elif len(matching) == 2:
            reasons.append(f"offers {matching[0]} and {matching[1]} from your interests")
        else:
            reasons.append(f"offers {', '.join(matching[:-1])}, and {matching[-1]} from your interests")

    if not reasons:
        return ""

    if len(reasons) == 1:
        return f"Recommended because {reasons[0]}."
    elif len(reasons) == 2:
        return f"Recommended because {reasons[0]}, and {reasons[1]}."
    else:
        joined = ', '.join(reasons[:-1])
        return f"Recommended because {joined}, and {reasons[-1]}."


def _annotated_destinations():
    # Single query fetching all destinations with rating stats pre-computed,
    # avoiding the N+1 that DestinationSerializer's average_rating/
    # review_count fields would otherwise incur per destination. select_related
    # joins travel_type/best_season in the same query - both the scoring
    # explanation text and DestinationSerializer's SlugRelatedField output
    # read these, so without this every scored/serialized destination would
    # trigger its own extra query for each FK.
    return Destination.objects.select_related('travel_type', 'best_season').annotate(
        avg_rating_annotated=Avg('reviews__rating'),
        review_count_annotated=Count('reviews', distinct=True),
    )


def _serializer_context(request):
    context = {'request': request}
    user = request.user
    if user.is_authenticated:
        context['favorited_ids'] = set(user.favorite_destinations.values_list('id', flat=True))
        context['wishlisted_ids'] = set(user.wishlist_destinations.values_list('id', flat=True))
        context['visited_ids'] = set(user.visited_destinations.values_list('id', flat=True))
    return context


def _score_and_serialize(destinations, prefs, request):
    scored = []
    for dest in destinations:
        similarity, breakdown = score_destination(dest, prefs)
        if similarity >= SIMILARITY_THRESHOLD:
            scored.append((similarity, breakdown, dest))

    scored.sort(key=lambda item: item[0], reverse=True)

    serializer = DestinationSerializer(
        [item[2] for item in scored],
        many=True,
        context=_serializer_context(request),
    )

    results = []
    for i, item in enumerate(scored):
        data = dict(serializer.data[i])
        data['score'] = round(item[0], 4)
        data['score_breakdown'] = item[1]
        data['match_explanation'] = generate_explanation(item[2], prefs, item[1])
        data['match_quality'] = match_quality_label(item[0])
        results.append(data)

    return results


def _preferences_snapshot(user):
    return {
        'travel_type': user.preferred_travel_type.slug if user.preferred_travel_type_id else None,
        'season': user.preferred_season.slug if user.preferred_season_id else None,
        'activities': list(user.preferred_activities or []),
        'budget': str(user.budget) if user.budget else None,
        'trip_duration_preference': user.trip_duration_preference,
    }


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Recomputed from request.user's current preference fields on every
        # call (no caching), so recommendations always reflect the latest
        # saved preferences - no extra invalidation step is needed when a
        # user updates their profile.
        results = _score_and_serialize(_annotated_destinations(), request.user, request)
        try:
            RecommendationHistory.objects.create(
                user=request.user,
                preferences_snapshot=_preferences_snapshot(request.user),
                results_snapshot=[
                    {
                        'destination_id': r['id'], 'name': r['name'], 'name_mk': r['name_mk'], 'slug': r['slug'],
                        'score': r['score'], 'match_quality': r['match_quality'],
                    }
                    for r in results[:10]
                ],
                result_count=len(results),
            )
        except Exception:
            # A history-log write failing must never break the actual
            # recommendation response the user is waiting on.
            pass
        return Response({'count': len(results), 'results': results})


class RecommendationHistoryListView(generics.ListAPIView):
    serializer_class = RecommendationHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecommendationHistory.objects.filter(user=self.request.user)
