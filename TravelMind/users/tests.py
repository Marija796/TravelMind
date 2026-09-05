import json
from unittest.mock import MagicMock, patch

from django.core import mail
from django.test import TestCase
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APITestCase
from rest_framework import status

from destinations.models import TravelCategory, Destination
from reviews.models import Review
from .models import CustomUser
from .utils import email_verification_token
from .vectors import calculate_similarity


def make_destination(**overrides):
    category, _ = TravelCategory.objects.get_or_create(slug='beach', defaults={'name': 'Beach'})
    defaults = {
        'name': 'Test City', 'country': 'Testland', 'description': 'A place.',
        'travel_type': category, 'estimated_cost': 500, 'slug': 'test-city',
    }
    defaults.update(overrides)
    return Destination.objects.create(**defaults)


class RegistrationAndVerificationTests(APITestCase):
    def test_register_creates_unverified_user_and_sends_email(self):
        resp = self.client.post('/api/users/register/', {
            'username': 'newtraveler', 'email': 'newtraveler@example.com',
            'password': 'StrongPass123', 'password2': 'StrongPass123',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        user = CustomUser.objects.get(username='newtraveler')
        self.assertFalse(user.is_verified)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('verify', mail.outbox[0].subject.lower())
        self.assertIn('/verify-email?uid=', mail.outbox[0].body)

    def test_unverified_user_cannot_log_in(self):
        user = CustomUser.objects.create_user(username='pending', email='pending@example.com', password='StrongPass123')
        self.assertFalse(user.is_verified)

        resp = self.client.post('/api/users/login/', {'username': 'pending', 'password': 'StrongPass123'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(resp.data.get('code'), 'email_not_verified')

    def test_verify_email_with_valid_token_allows_login(self):
        user = CustomUser.objects.create_user(username='verifyme', email='verifyme@example.com', password='StrongPass123')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)

        resp = self.client.post('/api/users/verify-email/', {'uid': uid, 'token': token})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.is_verified)

        login_resp = self.client.post('/api/users/login/', {'username': 'verifyme', 'password': 'StrongPass123'})
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_resp.data)

    def test_verify_email_rejects_invalid_token(self):
        user = CustomUser.objects.create_user(username='badtoken', email='badtoken@example.com', password='StrongPass123')
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        resp = self.client.post('/api/users/verify-email/', {'uid': uid, 'token': 'not-a-real-token'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_verified)

    def test_verify_email_twice_is_idempotent_not_an_error(self):
        user = CustomUser.objects.create_user(username='twice', email='twice@example.com', password='StrongPass123')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)

        first = self.client.post('/api/users/verify-email/', {'uid': uid, 'token': token})
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        second = self.client.post('/api/users/verify-email/', {'uid': uid, 'token': token})
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertIn('already verified', second.data['message'].lower())

    def test_resend_verification_does_not_reveal_whether_email_exists(self):
        resp_unknown = self.client.post('/api/users/resend-verification/', {'email': 'nobody@example.com'})
        self.assertEqual(resp_unknown.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

        CustomUser.objects.create_user(username='resendme', email='resendme@example.com', password='StrongPass123')
        resp_known = self.client.post('/api/users/resend-verification/', {'email': 'resendme@example.com'})
        self.assertEqual(resp_known.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_unknown.data, resp_known.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_resend_verification_is_a_noop_for_already_verified_user(self):
        user = CustomUser.objects.create_user(username='alreadyok', email='alreadyok@example.com', password='StrongPass123')
        user.is_verified = True
        user.save()

        self.client.post('/api/users/resend-verification/', {'email': 'alreadyok@example.com'})
        self.assertEqual(len(mail.outbox), 0)


class AdminLoginUnaffectedByVerificationTests(APITestCase):
    """Section 7 of the spec: admin login must never depend on is_verified."""

    def test_unverified_admin_can_log_in_via_admin_endpoint(self):
        admin = CustomUser.objects.create_user(
            username='boss', email='boss@example.com', password='StrongPass123', role='admin',
        )
        self.assertFalse(admin.is_verified)

        resp = self.client.post('/api/users/admin/login/', {'username': 'boss', 'password': 'StrongPass123'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)

    def test_non_admin_still_rejected_from_admin_endpoint_with_generic_error(self):
        CustomUser.objects.create_user(
            username='regular', email='regular@example.com', password='StrongPass123', is_verified=True,
        )
        resp = self.client.post('/api/users/admin/login/', {'username': 'regular', 'password': 'StrongPass123'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('code', resp.data)


class GoogleAndAdminCreatedUsersAreAutoVerifiedTests(APITestCase):
    def test_admin_created_user_is_verified_immediately(self):
        admin = CustomUser.objects.create_user(
            username='admin1', email='admin1@example.com', password='StrongPass123',
            role='admin', is_verified=True,
        )
        self.client.force_authenticate(admin)

        resp = self.client.post('/api/users/admin/users/create/', {
            'username': 'createdbyadmin', 'email': 'createdbyadmin@example.com', 'password': 'StrongPass123',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = CustomUser.objects.get(username='createdbyadmin')
        self.assertTrue(user.is_verified)

    # Simulates the implicit-flow path (see GoogleAuthView.post): the
    # frontend sends an OAuth access token as 'credential', which fails
    # id_token.verify_oauth2_token (it isn't a JWT) and falls back to the
    # userinfo-endpoint lookup - mocked here the same way, so this exercises
    # the exact branch a real "Continue with Google" click takes.
    @patch('users.views.urllib.request.urlopen')
    @patch('users.views.id_token.verify_oauth2_token', side_effect=ValueError('not a JWT'))
    def test_google_sign_in_verifies_a_pre_existing_unverified_account(self, mock_verify, mock_urlopen):
        # Registered the normal way, never clicked the verification link -
        # exactly the account state that a regular /login/ attempt would
        # reject with 'email_not_verified'.
        CustomUser.objects.create_user(
            username='pending2', email='pending2@example.com', password='StrongPass123',
        )

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            'email': 'pending2@example.com', 'name': 'Pending Two',
        }).encode()
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        resp = self.client.post('/api/users/google-auth/', {'credential': 'fake-access-token'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        user = CustomUser.objects.get(email='pending2@example.com')
        self.assertTrue(user.is_verified)

        # And a subsequent plain username/password login - previously
        # rejected - now succeeds, since Google sign-in already proved
        # ownership of the email address.
        login_resp = self.client.post(
            '/api/users/login/', {'username': 'pending2', 'password': 'StrongPass123'}
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)


class SimilarityFunctionTests(TestCase):
    def test_identical_users_score_highly(self):
        category, _ = TravelCategory.objects.get_or_create(slug='adventure', defaults={'name': 'Adventure'})
        a = CustomUser.objects.create_user(username='a', password='x', preferred_travel_type=category, budget=1000, trip_duration_preference=7)
        b = CustomUser.objects.create_user(username='b', password='x', preferred_travel_type=category, budget=1000, trip_duration_preference=7)
        score = calculate_similarity(a, b)
        self.assertGreater(score, 0.9)

    def test_users_with_no_comparable_data_score_zero(self):
        a = CustomUser.objects.create_user(username='a2', password='x')
        b = CustomUser.objects.create_user(username='b2', password='x')
        self.assertEqual(calculate_similarity(a, b), 0.0)

    def test_similarity_is_bounded_and_symmetric(self):
        cat_a, _ = TravelCategory.objects.get_or_create(slug='culture', defaults={'name': 'Culture'})
        cat_b, _ = TravelCategory.objects.get_or_create(slug='nature', defaults={'name': 'Nature'})
        a = CustomUser.objects.create_user(username='a3', password='x', preferred_travel_type=cat_a, budget=200)
        b = CustomUser.objects.create_user(username='b3', password='x', preferred_travel_type=cat_b, budget=5000)
        score_ab = calculate_similarity(a, b)
        score_ba = calculate_similarity(b, a)
        self.assertAlmostEqual(score_ab, score_ba, places=9)
        self.assertGreaterEqual(score_ab, 0.0)
        self.assertLessEqual(score_ab, 1.0)

    def test_shared_wishlist_increases_similarity(self):
        a = CustomUser.objects.create_user(username='wa', password='x')
        b = CustomUser.objects.create_user(username='wb', password='x')
        c = CustomUser.objects.create_user(username='wc', password='x')
        shared = make_destination(slug='shared-wishlist-dest')
        a.wishlist_destinations.add(shared)
        b.wishlist_destinations.add(shared)
        c.wishlist_destinations.add(make_destination(slug='unrelated-wishlist-dest', name='Unrelated'))

        self.assertGreater(calculate_similarity(a, b), calculate_similarity(a, c))

    def test_shared_high_ratings_increase_similarity(self):
        a = CustomUser.objects.create_user(username='ra', password='x')
        b = CustomUser.objects.create_user(username='rb', password='x')
        c = CustomUser.objects.create_user(username='rc', password='x')
        shared = make_destination(slug='shared-rated-dest')
        Review.objects.create(user=a, destination=shared, rating=5)
        Review.objects.create(user=b, destination=shared, rating=4)
        Review.objects.create(user=c, destination=make_destination(slug='unrelated-rated-dest', name='Unrelated2'), rating=5)

        self.assertGreater(calculate_similarity(a, b), calculate_similarity(a, c))

    def test_low_ratings_do_not_count_toward_rated_destinations_overlap(self):
        a = CustomUser.objects.create_user(username='lra', password='x')
        b = CustomUser.objects.create_user(username='lrb', password='x')
        shared = make_destination(slug='low-rated-dest')
        Review.objects.create(user=a, destination=shared, rating=2)
        Review.objects.create(user=b, destination=shared, rating=2)

        # Both rated it, but below RATING_LIKE_THRESHOLD - shouldn't count as
        # a "liked" overlap, and with nothing else comparable, similarity is 0.
        self.assertEqual(calculate_similarity(a, b), 0.0)


class DestinationInterestedUsersAuthTests(APITestCase):
    def test_requires_authentication(self):
        dest = make_destination()
        resp = self.client.get(f'/api/users/destinations/{dest.id}/interested/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class EngagementListViewTests(APITestCase):
    """FavoriteListView/WishlistListView/VisitedListView - regression tests
    for the N+1 query fix (now using the same annotated-queryset +
    serializer-context pattern as destinations/views.py, instead of serializing
    request.user.<x>_destinations.all() directly)."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='engager', password='x', is_verified=True)
        self.client.force_authenticate(self.user)

    def test_favorites_list_returns_only_favorited_destinations_with_correct_shape(self):
        favorited = make_destination(slug='fav-dest', name='Favorited')
        not_favorited = make_destination(slug='not-fav-dest', name='Not Favorited')
        self.user.favorite_destinations.add(favorited)
        Review.objects.create(user=self.user, destination=favorited, rating=5)

        resp = self.client.get('/api/users/favorites/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [d['id'] for d in resp.data]
        self.assertIn(favorited.id, ids)
        self.assertNotIn(not_favorited.id, ids)
        entry = next(d for d in resp.data if d['id'] == favorited.id)
        self.assertTrue(entry['is_favorited'])
        self.assertEqual(entry['review_count'], 1)
        self.assertEqual(entry['average_rating'], 5.0)

    def test_wishlist_list_returns_only_wishlisted_destinations(self):
        wishlisted = make_destination(slug='wish-dest', name='Wishlisted')
        self.user.wishlist_destinations.add(wishlisted)

        resp = self.client.get('/api/users/wishlist/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [d['id'] for d in resp.data]
        self.assertEqual(ids, [wishlisted.id])
        self.assertTrue(resp.data[0]['is_wishlisted'])

    def test_visited_list_returns_only_visited_destinations(self):
        visited = make_destination(slug='visited-dest', name='Visited')
        self.user.visited_destinations.add(visited)

        resp = self.client.get('/api/users/visited/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [d['id'] for d in resp.data]
        self.assertEqual(ids, [visited.id])
        self.assertTrue(resp.data[0]['is_visited'])

    def test_favorites_list_query_count_stays_flat_as_destinations_grow(self):
        # Regression guard for the actual N+1 bug: query count for the
        # favorites list must not scale with the number of destinations
        # returned (select_related + annotations + id-set context should
        # keep this constant, not O(N)).
        for i in range(5):
            dest = make_destination(slug=f'fav-perf-{i}', name=f'Fav Perf {i}')
            self.user.favorite_destinations.add(dest)

        with self.assertNumQueries(4):
            # 1: favorites queryset, 2-4: favorited/wishlisted/visited id-set
            # context - flat regardless of how many favorites are returned.
            resp = self.client.get('/api/users/favorites/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 5)
