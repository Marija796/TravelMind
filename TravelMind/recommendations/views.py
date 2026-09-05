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
from django.db.models import Avg, Count, Q

from core.similarity import overlap_coefficient
from destinations.models import Destination
from destinations.serializers import DestinationSerializer
from users.models import CustomUser
from users.vectors import calculate_similarity, RATING_LIKE_THRESHOLD
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

# How much a destination's collaborative signal (similar users' favorites/
# visits) has to clear before it's worth recommending on that basis alone -
# same bar used to decide whether the "travelers with similar taste..."
# explanation line is worth showing.
SOCIAL_THRESHOLD = 0.3

# How much a destination's own liked/saved/rated/visited affinity score
# (_history_score, 0-1) has to clear before it's worth recommending on that
# basis alone, independent of whether it matches the user's explicit stated
# criteria - the "own data" mirror of SOCIAL_THRESHOLD. 0.5 means at least
# one of the two tracked signals (country, travel type) matches fully when
# both are available, or a full match on the one signal available when only
# one is - a real, specific echo of the user's own history, not a coincidence.
HISTORY_THRESHOLD = 0.5

# Own favorited/visited history is *supporting* evidence, not a stated
# preference - it should nudge a score up, never veto one down to 0 the way
# a genuine conflicting criterion (e.g. wrong travel_type) does. Kept small
# and deliberately not part of the multiplicative CRITERIA product below.
HISTORY_BOOST_WEIGHT = 0.08


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


def _has_hard_type_conflict(prefs, destination):
    """
    True when the user explicitly stated a preferred_travel_type and this
    destination's travel_type is a different one - a genuine, hard
    conflict (as opposed to _type_active(prefs) being False, which just
    means "no opinion stated" and isn't a conflict at all). See
    classify_recommendation for why this specifically blocks
    collaborative-only qualification.
    """
    return _type_active(prefs) and prefs.preferred_travel_type_id != destination.travel_type_id


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


def _history_active(prefs):
    # Set once per request by RecommendationView.get() (see
    # _attach_history_affinity) from everything the user has positively
    # engaged with - never queried per-destination, to avoid an N+1 here.
    return bool(getattr(prefs, '_history_countries', None) or getattr(prefs, '_history_travel_type_ids', None))


def _affinity_score(countries, type_ids, destination):
    signals = []
    if countries:
        signals.append(1.0 if destination.country in countries else 0.0)
    if type_ids:
        signals.append(1.0 if destination.travel_type_id in type_ids else 0.0)
    return sum(signals) / len(signals) if signals else 0.0


def _history_score(prefs, destination):
    """
    A destination scores well here if it shares a country or travel type
    with something the user has already favorited, wishlisted, rated
    RATING_LIKE_THRESHOLD+, or visited - the same "people who liked X also
    liked Y" signal used elsewhere in the app (DestinationInterestedUsersView),
    applied to destination-to-destination affinity instead of user-to-user.
    Only the two signals the user actually has history for are averaged, so
    a user with only a favorited country (no travel-type signal yet) isn't
    penalized for the missing half.

    This is the BROAD signal (all four engagement types) - used only as the
    small HISTORY_BOOST_WEIGHT ranking nudge in score_destination. It is
    deliberately NOT used to independently qualify a destination into the
    results (see _strong_history_score for that) - verified against real
    seeded data that a user who has rated dozens of destinations quickly
    ends up with history covering most of the catalog's countries/types
    (e.g. one seeded user's ratings alone spanned 29 of ~100 destinations'
    countries and 7 of the travel-type categories), which would flood
    "recommendations" into "most of the catalog" if this broad signal alone
    could qualify a destination the same way SOCIAL_THRESHOLD does.
    """
    countries = getattr(prefs, '_history_countries', None) or set()
    type_ids = getattr(prefs, '_history_travel_type_ids', None) or set()
    return _affinity_score(countries, type_ids, destination)


def _strong_history_score(prefs, destination):
    """
    The NARROW counterpart to _history_score: only favorited/visited (never
    wishlisted/rated) - a real, deliberate, typically-small set (a handful
    of destinations, not dozens), so it stays a meaningful, specific signal
    even for a user with a long rating history. This is what
    classify_recommendation checks against HISTORY_THRESHOLD to let a
    destination qualify purely on the user's own history, independent of
    their explicit stated preferences - the "own data" mirror of how
    SOCIAL_THRESHOLD lets collaborative filtering qualify a destination
    independent of everything else.
    """
    countries = getattr(prefs, '_strong_history_countries', None) or set()
    type_ids = getattr(prefs, '_strong_history_travel_type_ids', None) or set()
    return _affinity_score(countries, type_ids, destination)


def _attach_history_affinity(user):
    """
    Precomputes the countries/travel types of everything the user has
    positively engaged with, in two tiers, and stashes both directly on the
    user instance - keeps the per-destination scoring loop free of any extra
    queries:
      - _history_countries/_history_travel_type_ids: the BROAD set - also
        favorited ("liked"), wishlisted ("saved"), rated RATING_LIKE_THRESHOLD+
        ("rated"), or visited - read by _history_score.
      - _strong_history_countries/_strong_history_travel_type_ids: the
        NARROW set - favorited or visited only - read by _strong_history_score.
    """
    rows = Destination.objects.filter(
        Q(favorited_by=user) | Q(wishlisted_by=user) | Q(visited_by=user)
        | Q(reviews__user=user, reviews__rating__gte=RATING_LIKE_THRESHOLD)
    ).values('country', 'travel_type_id')
    user._history_countries = {r['country'] for r in rows if r['country']}
    user._history_travel_type_ids = {r['travel_type_id'] for r in rows if r['travel_type_id']}

    strong_rows = Destination.objects.filter(
        Q(favorited_by=user) | Q(visited_by=user)
    ).values('country', 'travel_type_id')
    user._strong_history_countries = {r['country'] for r in strong_rows if r['country']}
    user._strong_history_travel_type_ids = {r['travel_type_id'] for r in strong_rows if r['travel_type_id']}
    return user


# A wishlisted or highly-rated destination is a softer positive signal than
# an outright favorite or an actual visit, so it counts for half a "vote"
# when tallying a similar user's influence - see _attach_social_affinity.
SOCIAL_WEAK_SIGNAL_WEIGHT = 0.5

SOCIAL_SIMILAR_USERS_LIMIT = 8


def _social_score(prefs, destination):
    return getattr(prefs, '_social_scores', {}).get(destination.id, 0.0)


def _attach_social_affinity(user):
    """
    Real collaborative filtering: finds the user's most similar other users
    (the same calculate_similarity function used by DestinationInterestedUsersView
    and the admin Similar Users tool - never a separate/fake calculation),
    then treats every destination those similar users favorited, wishlisted,
    rated RATING_LIKE_THRESHOLD+, or visited as a "vote" weighted by how
    similar that user actually is. A destination favorited by several
    highly-similar users scores higher than one only a loosely-similar user
    has touched. Scores are capped at 1.0 - same ceiling pattern as
    MAX_MATCH_SCORE elsewhere in this module.

    Candidate selection and prefetching mirror _compute_similar_users in
    users/views.py (exclude self/admins/inactive accounts) so this can't
    drift from what the rest of the app considers a valid "similar user".
    Runs once per request, not per destination, to avoid an N+1 here.
    """
    my_favorites = set(user.favorite_destinations.values_list('id', flat=True))
    my_wishlist = set(user.wishlist_destinations.values_list('id', flat=True))
    my_rated = set(user.reviews.filter(rating__gte=RATING_LIKE_THRESHOLD).values_list('destination_id', flat=True))
    others = CustomUser.objects.exclude(pk=user.pk).exclude(role='admin').filter(
        is_active=True, is_staff=False, is_superuser=False,
    ).prefetch_related('favorite_destinations', 'wishlist_destinations', 'visited_destinations', 'reviews')

    scored_others = []
    for other in others:
        other_favorites = {d.id for d in other.favorite_destinations.all()}
        other_wishlist = {d.id for d in other.wishlist_destinations.all()}
        other_rated = {r.destination_id for r in other.reviews.all() if r.rating >= RATING_LIKE_THRESHOLD}
        similarity = calculate_similarity(
            user, other, favorites_a=my_favorites, favorites_b=other_favorites,
            wishlist_a=my_wishlist, wishlist_b=other_wishlist, rated_a=my_rated, rated_b=other_rated,
        )
        if similarity > 0:
            scored_others.append((similarity, other))
    scored_others.sort(key=lambda item: item[0], reverse=True)
    top_similar = scored_others[:SOCIAL_SIMILAR_USERS_LIMIT]

    votes = {}
    for similarity, other in top_similar:
        # Favorited/visited is certain, explicit positive engagement - full
        # vote weight. Wishlisted/highly-rated is a softer signal (verified
        # against real seeded data: some users have rated dozens of
        # destinations 4-5 stars but favorited only a handful - without this
        # split, one prolific rater among the top-N similar users could push
        # a large fraction of the entire catalog just over SOCIAL_THRESHOLD,
        # diluting "recommended" into "most of the catalog"). Never
        # double-counted when a destination is both (e.g. favorited AND
        # rated) - strong_ids wins via the set difference below.
        strong_ids = {d.id for d in other.favorite_destinations.all()} | {d.id for d in other.visited_destinations.all()}
        weak_ids = (
            {d.id for d in other.wishlist_destinations.all()}
            | {r.destination_id for r in other.reviews.all() if r.rating >= RATING_LIKE_THRESHOLD}
        ) - strong_ids
        for dest_id in strong_ids:
            votes[dest_id] = votes.get(dest_id, 0.0) + similarity
        for dest_id in weak_ids:
            votes[dest_id] = votes.get(dest_id, 0.0) + similarity * SOCIAL_WEAK_SIGNAL_WEIGHT

    user._social_scores = {dest_id: min(1.0, total) for dest_id, total in votes.items()}
    return user


# Relative importance of each EXPLICIT preference criterion (destination
# type and budget matter most; secondary preferences matter less) - also
# used as the geometric mean's normalized exponents and as the basis for
# the confidence factor.
#
# Deliberately limited to the preferences the user actually stated. Earlier
# versions of this module also multiplied 'history' (own favorited/visited
# affinity) and 'social' (similar users' favorites/visits) into this same
# product - that was a bug, not just a design choice: is_active() for both
# is a per-USER flag ("do I have any history/similar-user data at all"),
# but the per-destination score is legitimately 0.0 for the vast majority
# of destinations that simply aren't covered by that data (no shared
# country, not in anyone's favorites). Because the geometric mean multiplies
# every active criterion's score together, a single legitimate 0.0 on a
# criterion that only means "no extra evidence" (not "conflict") collapsed
# the ENTIRE score to 0 - so as soon as a user had any collaborative data,
# almost every otherwise-good preference match vanished. Verified against
# real seeded data: 95-100 of ~100 candidate destinations scored exactly
# 0.0 for most users once 'social' had any votes at all.
#
# 'history' is now folded in as a small additive boost (HISTORY_BOOST_WEIGHT,
# see score_destination) that can only raise a score, never zero it. 'social'
# is handled entirely separately as its own collaborative-filtering signal
# and merged with this preference score in _score_and_serialize - see
# classify_recommendation.
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
    """Returns (realistic preference-based match score in [0, MAX_MATCH_SCORE],
    human-readable breakdown dict). This is the content-based half of the
    hybrid system - see classify_recommendation for how it's combined with
    the collaborative (similar-users) signal."""
    active = [c for c in CRITERIA if c.is_active(user)]
    if active:
        active_weight = sum(c.weight for c in active)
        raw_score = math.prod(
            c.score(user, destination) ** (c.weight / active_weight) for c in active
        )
        confidence = _confidence_factor(active)
        base = raw_score * confidence
    else:
        base = 0.0

    if _history_active(user):
        base += HISTORY_BOOST_WEIGHT * _history_score(user, destination)

    similarity = min(base, MAX_MATCH_SCORE)
    breakdown = _dimension_breakdown(destination, user)
    return similarity, breakdown


def classify_recommendation(destination, user):
    """
    The hybrid combination step: merges the content-based preference score
    with the independent collaborative (similar-users) score instead of
    multiplying them together, so a destination can earn its place in the
    results via EITHER signal - a strong preference match with zero
    collaborative signal still surfaces, and a destination with no
    preference-criteria overlap but a strong collaborative signal still
    surfaces too (which is the whole point of collaborative filtering -
    discovering things outside what the user explicitly stated).

    "Own preferences" itself has two independent qualification paths, kept
    symmetric with how collaborative filtering already worked: the explicit
    stated-criteria score (pref_score, via SIMILARITY_THRESHOLD) AND the
    user's own STRONG history affinity score (via HISTORY_THRESHOLD) - not
    just the small HISTORY_BOOST_WEIGHT nudge folded into pref_score inside
    score_destination, which can only fine-tune ranking among destinations
    that already clear SIMILARITY_THRESHOLD and can never by itself cross
    that bar. Without this, a destination sharing a country/type with
    something the user personally favorited or visited - but not matching
    their stated type/budget/season - would never surface from "their own
    data" at all, even though the spec explicitly calls out "places they
    liked ... or visited" as part of the preferences-based source, not just
    the collaborative one. Verified against real seeded data before adding
    this: dozens of such destinations per user were being silently excluded.

    Uses _strong_history_score (favorited/visited only), not the broader
    _history_score (which also includes wishlisted/rated), for this
    independent qualification check - also verified against real seeded
    data: a user with a long rating history (dozens of destinations rated,
    spanning most of the catalog's countries/travel types) made the broad
    signal qualify almost the entire remaining catalog, which isn't a
    meaningful "recommendation" anymore. Favorited/visited stays a small,
    deliberate set, so it stays a specific signal even for a prolific rater.

    Returns (final_score, breakdown, source) where source is 'preference'
    (either "own data" path), 'collaborative', or 'hybrid' (clears an "own
    data" bar and the collaborative bar) - or None if nothing clears any
    threshold. When a user has no history/similar-user data at all, the
    respective score is 0.0 for every destination and this transparently
    falls back to pure explicit-preference recommendations - no separate
    "not enough data" branch needed.

    EXCEPTION: a destination whose travel_type flatly conflicts with the
    user's explicitly stated preferred_travel_type can't qualify through
    EITHER soft signal - collaborative (similar users) or the user's own
    STRONG history - alone (see _has_hard_type_conflict). Both are real
    bugs this fixes, same root cause, two different data paths:

    - Collaborative: for a user with little/no engagement history yet,
      "similar users" (_attach_social_affinity, via calculate_similarity)
      can be determined almost entirely from *declared* preference overlap
      rather than actual shared taste in destinations - e.g. two users who
      both merely picked 'beach' count as similar even with zero
      destinations in common. That thin signal was then enough, on its
      own, to recommend a completely unrelated destination (verified
      against real seeded data: a user who set
      travel_type='beach'/activities=['Surfing'] and had no
      favorites/wishlist/ratings yet was recommended Paris and Tokyo -
      both 'city' destinations - purely because some other
      'beach'-preferring user happened to have favorited/rated them for
      unrelated reasons).
    - Own history: qualifies_history only requires sharing a country OR a
      travel_type with something the user favorited/visited in the past
      (see _affinity_score) - a travel_type match alone is enough, and a
      user's *past* engagement can easily predate or simply differ from
      their *current* stated preference. Verified against real seeded
      data: a user who now has preferred_travel_type='beach' but had
      previously favorited/visited a 'mountain' destination (Dolomites)
      was recommended Banff - also 'mountain', in Canada rather than
      Italy - as their #1 match, purely because it shared that one
      travel_type with the old favorite, entirely contradicting the
      'beach' preference they'd since set.

    Note qualifies_pref can never independently qualify a hard-conflicting
    destination in the first place - a mismatched type_score of 0.0
    collapses the whole CRITERIA product to 0 in score_destination - so
    this guard only ever has to zero out the two soft signals, never the
    explicit-preference one.

    An explicit stated preference is a hard constraint the user typed in
    themselves; "similar users liked it" and "you liked something similar
    once" are both soft signals and must not silently override it.
    Collaborative/history picks still surface freely for anything the
    user hasn't explicitly constrained.
    """
    pref_score, breakdown = score_destination(destination, user)
    strong_history_score = _strong_history_score(user, destination)
    social_score = _social_score(user, destination)

    qualifies_pref = pref_score >= SIMILARITY_THRESHOLD
    qualifies_history = strong_history_score >= HISTORY_THRESHOLD
    qualifies_social = social_score >= SOCIAL_THRESHOLD
    if not qualifies_pref and _has_hard_type_conflict(user, destination):
        qualifies_history = False
        qualifies_social = False
    own_qualifies = qualifies_pref or qualifies_history
    if not (own_qualifies or qualifies_social):
        return None

    if own_qualifies and qualifies_social:
        source = 'hybrid'
    elif qualifies_social:
        source = 'collaborative'
    else:
        source = 'preference'

    own_score = max(pref_score, strong_history_score)
    final_score = min(max(own_score, social_score), MAX_MATCH_SCORE)
    return final_score, breakdown, source


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


def _match_caveat(destination, user):
    """
    A single, concise clause naming the most important explicitly-stated
    preference this destination falls short on - mirrors CRITERIA's
    weighted priority order (type > budget > season > activities >
    duration), so the caveat always names the *most* important gap rather
    than an unprioritized list of every minor one. Returns "" when the
    destination meets every criterion the user actually stated an opinion
    on - a near-perfect match doesn't need a hedge. Used to give the same
    "strong match, but X" honesty a human recommender would give, instead
    of only ever listing positives.
    """
    if _type_active(user) and _type_score(user, destination) < 1.0:
        return "it's not your usual travel style"
    if _budget_active(user) and _budget_score(user, destination) < 1.0:
        over_by = float(destination.estimated_cost or 0) - float(user.budget)
        return f"it runs about ${int(over_by):,} over your stated budget"
    if _season_active(user) and _season_score(user, destination) < 1.0:
        return "it isn't at its best during your preferred season"
    if _activities_active(user) and _activities_score(user, destination) < 1.0:
        return "it only covers some of your preferred activities"
    if _duration_active(user) and _duration_score(user, destination) < 1.0:
        return "its typical trip length doesn't quite match what you prefer"
    return ""


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

    history_countries = getattr(user, '_history_countries', None) or set()
    history_type_ids = getattr(user, '_history_travel_type_ids', None) or set()
    if destination.country in history_countries:
        reasons.append(f"is in {destination.country}, like places you've liked, saved, rated, or visited")
    elif destination.travel_type_id in history_type_ids:
        reasons.append("matches the travel style of places you've liked, saved, rated, or visited")

    social_score = getattr(user, '_social_scores', {}).get(destination.id, 0.0)
    if social_score >= SOCIAL_THRESHOLD:
        reasons.append("travelers with similar taste to you have liked, saved, rated, or visited it")

    if not reasons:
        return ""

    if len(reasons) == 1:
        sentence = f"Recommended because {reasons[0]}"
    elif len(reasons) == 2:
        sentence = f"Recommended because {reasons[0]}, and {reasons[1]}"
    else:
        joined = ', '.join(reasons[:-1])
        sentence = f"Recommended because {joined}, and {reasons[-1]}"

    # An honest recommendation names its biggest gap too, not just its
    # strengths - see _match_caveat. Only one (the most important) gap is
    # named, to stay as concise as the positive reasons above.
    caveat = _match_caveat(destination, user)
    if caveat:
        sentence += f", though {caveat}"

    return sentence + "."


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
        classified = classify_recommendation(dest, prefs)
        if classified is not None:
            score, breakdown, source = classified
            scored.append((score, breakdown, dest, source))

    # Primary key: the match score, rounded to the same precision it's
    # displayed at (see data['score'] below) - two destinations that show
    # the same percentage to the user should never appear to be ordered
    # arbitrarily. When scores tie (or round to the same displayed value),
    # break the tie using secondary preferences rather than leaving it to
    # incidental DB/query order: first by how many named criteria
    # (type/budget/season/activities - see _dimension_breakdown) actually
    # align, then by average rating as a last, genuinely-neutral
    # tiebreaker for the rare remaining exact tie.
    scored.sort(
        key=lambda item: (
            round(item[0], 4),
            sum(item[1].values()),
            item[2].avg_rating_annotated or 0,
        ),
        reverse=True,
    )

    serializer = DestinationSerializer(
        [item[2] for item in scored],
        many=True,
        context=_serializer_context(request),
    )

    results = []
    for i, item in enumerate(scored):
        score, breakdown, dest, source = item
        data = dict(serializer.data[i])
        data['score'] = round(score, 4)
        data['score_breakdown'] = breakdown
        data['match_explanation'] = generate_explanation(dest, prefs, breakdown)
        data['match_quality'] = match_quality_label(score)
        data['recommendation_source'] = source
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
        user = _attach_history_affinity(request.user)
        user = _attach_social_affinity(user)
        # A destination the user has already favorited or visited isn't a
        # useful "recommendation" - it's something they've already engaged
        # with. Wishlisted destinations are left in (a wishlist is "want to
        # go", not "already been"), so they can still legitimately surface.
        destinations = _annotated_destinations().exclude(
            Q(favorited_by=user) | Q(visited_by=user)
        )
        results = _score_and_serialize(destinations, user, request)
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
