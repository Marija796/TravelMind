from rest_framework.test import APITestCase
from rest_framework import status

from destinations.models import TravelCategory, Destination
from users.models import CustomUser
from reviews.models import Review
from .views import (
    score_destination, _attach_history_affinity, _attach_social_affinity, _social_score,
    _strong_history_score, classify_recommendation, SIMILARITY_THRESHOLD, SOCIAL_THRESHOLD, HISTORY_THRESHOLD,
)


def make_category(slug, name=None):
    return TravelCategory.objects.get_or_create(slug=slug, defaults={'name': name or slug.title()})[0]


def make_destination(slug, country, travel_type, **overrides):
    defaults = {
        'name': slug.replace('-', ' ').title(), 'country': country, 'description': 'A place.',
        'travel_type': travel_type, 'estimated_cost': 500, 'slug': slug,
    }
    defaults.update(overrides)
    return Destination.objects.create(**defaults)


class HistoryCriterionTests(APITestCase):
    """Section 12/13/18 of the spec: favorited/visited destination
    characteristics should influence future recommendation scores."""

    def setUp(self):
        self.beach = make_category('beach', 'Beach')
        self.mountain = make_category('mountain', 'Mountain')
        self.user = CustomUser.objects.create_user(username='traveler', password='x', is_verified=True)

    def test_destination_sharing_favorited_country_scores_higher(self):
        favorited = make_destination('paris', 'France', self.beach)
        self.user.favorite_destinations.add(favorited)

        same_country = make_destination('lyon', 'France', self.mountain)
        unrelated = make_destination('tokyo', 'Japan', self.mountain)

        user = _attach_history_affinity(CustomUser.objects.get(pk=self.user.pk))
        score_same, _ = score_destination(same_country, user)
        score_unrelated, _ = score_destination(unrelated, user)

        self.assertGreater(score_same, score_unrelated)

    def test_no_history_means_history_criterion_is_simply_inactive(self):
        dest = make_destination('oslo', 'Norway', self.beach)
        user = _attach_history_affinity(self.user)
        # Should not raise, and should not be scored as an active criterion
        # with no favorites/visits to draw from.
        score, _ = score_destination(dest, user)
        self.assertGreaterEqual(score, 0.0)

    def test_own_favorited_history_alone_qualifies_a_recommendation(self):
        """Regression test: own favorited/visited history must be able to
        independently qualify a destination into the results (source
        'preference'), not just nudge the ranking of destinations that
        already match explicit stated criteria. self.user here has NO
        explicit preferences set at all, so pref_score is always 0 -
        classify_recommendation must still return a result from history
        alone once it clears HISTORY_THRESHOLD."""
        favorited = make_destination('paris', 'France', self.beach)
        self.user.favorite_destinations.add(favorited)
        same_country = make_destination('lyon', 'France', self.mountain)

        user = _attach_history_affinity(CustomUser.objects.get(pk=self.user.pk))
        pref_score, _ = score_destination(same_country, user)
        self.assertLess(pref_score, SIMILARITY_THRESHOLD)  # no explicit-criteria match at all

        result = classify_recommendation(same_country, user)
        self.assertIsNotNone(result)
        final_score, _, source = result
        self.assertEqual(source, 'preference')
        self.assertGreaterEqual(final_score, HISTORY_THRESHOLD)

    def test_own_history_pick_is_blocked_by_a_hard_travel_type_conflict(self):
        """Regression test for a real-world bug: own past history must not
        override a *current*, explicitly stated travel_type preference -
        the same hard-conflict guard that already blocks the collaborative
        signal (see SocialCriterionTests) applies here too, for the same
        reason. Verified against real seeded data: a user who now has
        preferred_travel_type='beach' but had previously favorited a
        'mountain' destination (Dolomites, Italy) was recommended Banff -
        also 'mountain', but in Canada rather than Italy - as their #1
        match, purely because it shared that one travel_type with the old
        favorite, directly contradicting the 'beach' preference they'd
        since set. A user's past engagement predating (or simply
        differing from) their current stated preference is a soft signal,
        not proof the conflict doesn't matter."""
        self.user.preferred_travel_type = self.beach
        self.user.save(update_fields=['preferred_travel_type'])

        old_favorite = make_destination('dolomites', 'Italy', self.mountain)
        self.user.favorite_destinations.add(old_favorite)
        conflicting_type_dest = make_destination('banff', 'Canada', self.mountain)

        user = _attach_history_affinity(CustomUser.objects.get(pk=self.user.pk))
        pref_score, _ = score_destination(conflicting_type_dest, user)
        # Wrong travel_type means no *explicit-criteria* match (the small
        # nonzero value here is only score_destination's own
        # HISTORY_BOOST_WEIGHT nudge - see its docstring - which can
        # fine-tune ranking but never independently clear
        # SIMILARITY_THRESHOLD on its own).
        self.assertLess(pref_score, SIMILARITY_THRESHOLD)
        # The (stronger) strong-history signal alone clears HISTORY_THRESHOLD
        # - proving this destination would previously have been recommended
        # purely off that soft signal, were it not for the hard-conflict
        # guard below.
        self.assertGreaterEqual(_strong_history_score(user, conflicting_type_dest), HISTORY_THRESHOLD)

        self.assertIsNone(classify_recommendation(conflicting_type_dest, user))

    def test_wishlisted_or_rated_only_does_not_independently_qualify(self):
        """The narrower counterpart: a destination reachable only via
        wishlist/rating (never favorited/visited) should NOT by itself
        clear HISTORY_THRESHOLD - only favorited/visited is a strong enough,
        naturally-small signal for that (see _strong_history_score's
        docstring for why: real seeded data showed the broader signal,
        which also includes wishlist/ratings, floods almost the entire
        catalog for a user with a long rating history)."""
        rated = make_destination('hanoi', 'Vietnam', self.beach)
        Review.objects.create(user=self.user, destination=rated, rating=5)
        same_country = make_destination('hue', 'Vietnam', self.mountain)

        user = _attach_history_affinity(CustomUser.objects.get(pk=self.user.pk))
        self.assertIsNone(classify_recommendation(same_country, user))

    def test_wishlisted_country_boosts_score_even_without_a_favorite(self):
        wishlisted = make_destination('marrakesh', 'Morocco', self.beach)
        self.user.wishlist_destinations.add(wishlisted)

        same_country = make_destination('casablanca', 'Morocco', self.mountain)
        unrelated = make_destination('lima', 'Peru', self.mountain)

        user = _attach_history_affinity(CustomUser.objects.get(pk=self.user.pk))
        score_same, _ = score_destination(same_country, user)
        score_unrelated, _ = score_destination(unrelated, user)

        self.assertGreater(score_same, score_unrelated)

    def test_highly_rated_country_boosts_score_even_without_a_favorite(self):
        rated = make_destination('hanoi', 'Vietnam', self.beach)
        Review.objects.create(user=self.user, destination=rated, rating=5)

        same_country = make_destination('hue', 'Vietnam', self.mountain)
        unrelated = make_destination('quito', 'Ecuador', self.mountain)

        user = _attach_history_affinity(CustomUser.objects.get(pk=self.user.pk))
        score_same, _ = score_destination(same_country, user)
        score_unrelated, _ = score_destination(unrelated, user)

        self.assertGreater(score_same, score_unrelated)

    def test_low_rating_does_not_count_as_positive_history(self):
        disliked = make_destination('venice', 'Italy', self.beach)
        Review.objects.create(user=self.user, destination=disliked, rating=2)

        user = _attach_history_affinity(CustomUser.objects.get(pk=self.user.pk))
        self.assertNotIn('Italy', getattr(user, '_history_countries', set()))


class SocialCriterionTests(APITestCase):
    """Collaborative filtering: destinations favorited/visited by users
    similar to the current user (via the same calculate_similarity function
    used elsewhere in the app) should score higher than untouched ones.

    These test the collaborative signal (_social_score) and its combination
    with the preference score (classify_recommendation) directly, rather
    than through score_destination - score_destination is purely the
    content-based/preference half of the hybrid system now; folding social
    into it via the old multiplicative CRITERIA product was the actual bug
    (see the CRITERIA comment in views.py): a per-user "is there any social
    data at all" flag combined with a per-destination score that's
    legitimately 0.0 for un-favorited destinations collapsed the ENTIRE
    score to 0 for almost everything, everywhere, in the "For You" page."""

    def setUp(self):
        self.beach = make_category('beach3', 'Beach')
        self.user = CustomUser.objects.create_user(
            username='me', password='x', is_verified=True, preferred_travel_type=self.beach,
        )

    def test_destination_favorited_by_similar_user_scores_higher(self):
        similar_other = CustomUser.objects.create_user(
            username='similar_other', password='x', is_verified=True, preferred_travel_type=self.beach,
        )
        liked_by_similar = make_destination('bali', 'Indonesia', self.beach)
        similar_other.favorite_destinations.add(liked_by_similar)

        untouched = make_destination('helsinki', 'Finland', self.beach)

        user = _attach_social_affinity(CustomUser.objects.get(pk=self.user.pk))
        self.assertGreater(_social_score(user, liked_by_similar), _social_score(user, untouched))

    def test_no_similar_users_means_social_score_is_zero(self):
        dest = make_destination('cairo', 'Egypt', self.beach)
        user = _attach_social_affinity(self.user)
        self.assertEqual(_social_score(user, dest), 0.0)

    def test_destination_wishlisted_by_similar_user_scores_higher(self):
        similar_other = CustomUser.objects.create_user(
            username='similar_wishlist', password='x', is_verified=True, preferred_travel_type=self.beach,
        )
        wishlisted_by_similar = make_destination('lisbon', 'Portugal', self.beach)
        similar_other.wishlist_destinations.add(wishlisted_by_similar)

        untouched = make_destination('warsaw', 'Poland', self.beach)

        user = _attach_social_affinity(CustomUser.objects.get(pk=self.user.pk))
        self.assertGreater(_social_score(user, wishlisted_by_similar), _social_score(user, untouched))

    def test_destination_highly_rated_by_similar_user_scores_higher(self):
        similar_other = CustomUser.objects.create_user(
            username='similar_rater', password='x', is_verified=True, preferred_travel_type=self.beach,
        )
        rated_by_similar = make_destination('nairobi', 'Kenya', self.beach)
        Review.objects.create(user=similar_other, destination=rated_by_similar, rating=5)

        untouched = make_destination('dublin', 'Ireland', self.beach)

        user = _attach_social_affinity(CustomUser.objects.get(pk=self.user.pk))
        self.assertGreater(_social_score(user, rated_by_similar), _social_score(user, untouched))

    def test_low_rating_by_similar_user_does_not_count_as_a_vote(self):
        similar_other = CustomUser.objects.create_user(
            username='similar_low_rater', password='x', is_verified=True, preferred_travel_type=self.beach,
        )
        poorly_rated = make_destination('brasilia', 'Brazil', self.beach)
        Review.objects.create(user=similar_other, destination=poorly_rated, rating=2)

        user = _attach_social_affinity(CustomUser.objects.get(pk=self.user.pk))
        self.assertEqual(_social_score(user, poorly_rated), 0.0)

    def test_dissimilar_user_favorites_do_not_boost_score(self):
        mountain = make_category('mountain3', 'Mountain')
        dissimilar_other = CustomUser.objects.create_user(
            username='dissimilar_other', password='x', is_verified=True, preferred_travel_type=mountain,
        )
        # Only comparable criterion is travel_type, and it conflicts (beach
        # vs mountain), so calculate_similarity is exactly 0.0 - this user
        # shouldn't count as "similar" and their favorite shouldn't
        # influence scoring at all.
        favorited_by_dissimilar = make_destination('quito', 'Ecuador', mountain)
        dissimilar_other.favorite_destinations.add(favorited_by_dissimilar)

        user = _attach_social_affinity(CustomUser.objects.get(pk=self.user.pk))
        self.assertNotIn(favorited_by_dissimilar.id, getattr(user, '_social_scores', {}))

    def test_collaborative_pick_is_blocked_by_a_hard_travel_type_conflict(self):
        """Regression test for a real-world bug: a destination whose
        travel_type flatly conflicts with the user's explicitly stated
        preference must NOT be recommended off the collaborative signal
        alone - even when a 'similar' user favorited it, and even when
        that user only counts as 'similar' because they happen to share
        the same declared travel_type, not because they share any actual
        destination taste (see calculate_similarity's preference-only
        fallback when neither user has favorites/wishlist/ratings yet).
        Verified against real seeded data: a user who set
        travel_type='beach'/activities=['Surfing'] and had no engagement
        history yet was recommended Paris and Tokyo - both 'city'
        destinations - purely because some other 'beach'-preferring user
        happened to have favorited/rated them for unrelated reasons. An
        explicit stated preference is a hard constraint the user typed in
        themselves; 'similar users liked it' is a soft signal and must not
        silently override it (see _has_hard_type_conflict)."""
        mountain = make_category('mountain4', 'Mountain')
        similar_other = CustomUser.objects.create_user(
            username='similar_other2', password='x', is_verified=True, preferred_travel_type=self.beach,
        )
        conflicting_type_dest = make_destination('kyoto', 'Japan', mountain)
        similar_other.favorite_destinations.add(conflicting_type_dest)

        user = _attach_social_affinity(CustomUser.objects.get(pk=self.user.pk))
        pref_score, _ = score_destination(conflicting_type_dest, user)
        self.assertEqual(pref_score, 0.0)  # wrong travel_type -> no preference match
        # The collaborative signal alone clears the bar - proving this
        # destination would previously have been recommended purely off
        # that soft signal, were it not for the hard-conflict guard below.
        self.assertGreaterEqual(_social_score(user, conflicting_type_dest), SOCIAL_THRESHOLD)

        self.assertIsNone(classify_recommendation(conflicting_type_dest, user))

    def test_collaborative_pick_still_surfaces_for_a_non_categorical_conflict(self):
        """The flip side of the guard above: collaborative filtering can
        still surface a destination that conflicts with a *softer* stated
        preference (budget) as long as it doesn't conflict with the
        explicit, categorical travel_type - discovering things outside
        what the user explicitly stated is still the point of
        collaborative filtering, just not when it means ignoring the one
        thing (travel_type) they were most explicit about."""
        self.user.budget = 100
        self.user.save(update_fields=['budget'])

        similar_other = CustomUser.objects.create_user(
            username='similar_other3', password='x', is_verified=True, preferred_travel_type=self.beach,
        )
        # Same travel_type as the user (no hard conflict) but wildly over budget.
        expensive_but_on_type = make_destination('santorini', 'Greece', self.beach, estimated_cost=5000)
        similar_other.favorite_destinations.add(expensive_but_on_type)

        user = _attach_social_affinity(CustomUser.objects.get(pk=self.user.pk))
        pref_score, _ = score_destination(expensive_but_on_type, user)
        self.assertLess(pref_score, SIMILARITY_THRESHOLD)  # way over budget -> no preference match

        result = classify_recommendation(expensive_but_on_type, user)
        self.assertIsNotNone(result)
        final_score, _, source = result
        self.assertEqual(source, 'collaborative')
        self.assertGreaterEqual(final_score, SOCIAL_THRESHOLD)


class RecommendationEndpointTests(APITestCase):
    def setUp(self):
        self.beach = make_category('beach2', 'Beach')
        self.user = CustomUser.objects.create_user(
            username='recuser', password='x', is_verified=True,
            preferred_travel_type=self.beach, budget=1000, trip_duration_preference=5,
        )
        self.client.force_authenticate(self.user)

    def test_already_favorited_destination_is_excluded_from_results(self):
        favorited = make_destination('malaga', 'Spain', self.beach, estimated_cost=400)
        self.user.favorite_destinations.add(favorited)

        resp = self.client.get('/api/recommendations/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [r['id'] for r in resp.data['results']]
        self.assertNotIn(favorited.id, ids)

    def test_already_visited_destination_is_excluded_from_results(self):
        visited = make_destination('rome', 'Italy', self.beach, estimated_cost=400)
        self.user.visited_destinations.add(visited)

        resp = self.client.get('/api/recommendations/')
        ids = [r['id'] for r in resp.data['results']]
        self.assertNotIn(visited.id, ids)

    def test_wishlisted_destination_is_not_excluded(self):
        wishlisted = make_destination('athens', 'Greece', self.beach, estimated_cost=400)
        self.user.wishlist_destinations.add(wishlisted)

        resp = self.client.get('/api/recommendations/')
        ids = [r['id'] for r in resp.data['results']]
        self.assertIn(wishlisted.id, ids)

    def test_low_scoring_destination_is_filtered_by_threshold(self):
        mountain = make_category('mountain2', 'Mountain')
        conflicting = make_destination(
            'antarctica', 'Antarctica', mountain, estimated_cost=50000,
        )
        resp = self.client.get('/api/recommendations/')
        ids = [r['id'] for r in resp.data['results']]
        self.assertNotIn(conflicting.id, ids)
        for r in resp.data['results']:
            self.assertGreaterEqual(r['score'], SIMILARITY_THRESHOLD)


class HybridRecommendationEndpointTests(APITestCase):
    """End-to-end regression test for the bug this hybrid rework fixes:
    before it, any user with collaborative (similar-users) data at all saw
    almost every one of their own preference-based matches silently vanish
    from /api/recommendations/, because the old design multiplied the
    collaborative score into the same product as the preference criteria."""

    def setUp(self):
        self.beach = make_category('beach4', 'Beach')
        self.mountain = make_category('mountain5', 'Mountain')
        self.user = CustomUser.objects.create_user(
            username='hybriduser', password='x', is_verified=True,
            preferred_travel_type=self.beach, budget=1000,
        )
        self.client.force_authenticate(self.user)

    def test_results_mix_preference_and_collaborative_sources(self):
        # Matches the user's own stated preferences directly.
        preference_match = make_destination('barcelona', 'Spain', self.beach, estimated_cost=400)

        # A similar user (shares travel_type, so calculate_similarity > 0)
        # favorited a same-type destination that's way over the user's
        # stated budget - the user's own stated preferences alone would
        # never surface this (budget_fit fails); only the collaborative
        # signal can. Deliberately NOT a different travel_type here - see
        # test_collaborative_pick_is_blocked_by_a_hard_travel_type_conflict
        # in SocialCriterionTests for why a categorical conflict like that
        # must not be recommended off the collaborative signal alone.
        similar_other = CustomUser.objects.create_user(
            username='hybrid_similar', password='x', is_verified=True, preferred_travel_type=self.beach,
        )
        collaborative_only_match = make_destination('zermatt', 'Switzerland', self.beach, estimated_cost=20000)
        similar_other.favorite_destinations.add(collaborative_only_match)

        resp = self.client.get('/api/recommendations/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results_by_id = {r['id']: r for r in resp.data['results']}

        self.assertIn(preference_match.id, results_by_id)
        self.assertEqual(results_by_id[preference_match.id]['recommendation_source'], 'preference')

        self.assertIn(collaborative_only_match.id, results_by_id)
        self.assertEqual(results_by_id[collaborative_only_match.id]['recommendation_source'], 'collaborative')

    def test_no_collaborative_data_falls_back_to_pure_preference_results(self):
        preference_match = make_destination('valencia', 'Spain', self.beach, estimated_cost=400)

        resp = self.client.get('/api/recommendations/')
        results_by_id = {r['id']: r for r in resp.data['results']}

        self.assertIn(preference_match.id, results_by_id)
        self.assertEqual(results_by_id[preference_match.id]['recommendation_source'], 'preference')
        self.assertTrue(all(r['recommendation_source'] == 'preference' for r in resp.data['results']))
