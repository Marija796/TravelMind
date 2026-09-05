from unittest import TestCase as PlainTestCase

from rest_framework.test import APITestCase
from rest_framework import status

from destinations.models import Destination, TravelCategory
from users.models import CustomUser
from reviews.models import Review
from .similarity import cosine_similarity, overlap_coefficient


class OverlapCoefficientTests(PlainTestCase):
    def test_full_overlap_scores_one_regardless_of_larger_set_size(self):
        small = {'hiking', 'diving'}
        large = {'hiking', 'diving', 'museums', 'food', 'shopping'}
        self.assertEqual(overlap_coefficient(small, large), 1.0)

    def test_no_overlap_scores_zero(self):
        self.assertEqual(overlap_coefficient({'hiking'}, {'shopping'}), 0.0)

    def test_empty_set_scores_zero_not_an_error(self):
        self.assertEqual(overlap_coefficient(set(), {'hiking'}), 0.0)
        self.assertEqual(overlap_coefficient({'hiking'}, set()), 0.0)
        self.assertEqual(overlap_coefficient(set(), set()), 0.0)

    def test_partial_overlap_divides_by_smaller_set(self):
        # intersection {hiking} = 1, smaller set size = 2 -> 0.5
        self.assertEqual(overlap_coefficient({'hiking', 'diving'}, {'hiking', 'museums', 'food'}), 0.5)


class CosineSimilarityTests(PlainTestCase):
    def test_identical_vectors_score_one(self):
        self.assertAlmostEqual(cosine_similarity([1, 2, 3], [1, 2, 3]), 1.0)

    def test_zero_magnitude_vector_scores_zero_not_a_division_error(self):
        self.assertEqual(cosine_similarity([0, 0, 0], [1, 2, 3]), 0.0)

    def test_mismatched_length_raises(self):
        with self.assertRaises(ValueError):
            cosine_similarity([1, 2], [1, 2, 3])

    def test_orthogonal_vectors_score_zero(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)


class IsAdminRolePermissionTests(APITestCase):
    """core/permissions.py:IsAdminRole gates every admin-only endpoint in
    the app - exercised here through a real admin-only view
    (core/admin_views.py:AdminStatsView) rather than testing the permission
    class in isolation, so a regression here is caught the same way a real
    request would hit it."""

    def test_unauthenticated_request_is_rejected(self):
        resp = self.client.get('/api/admin/stats/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_is_forbidden(self):
        user = CustomUser.objects.create_user(username='notadmin', password='x', is_verified=True)
        self.client.force_authenticate(user)
        resp = self.client.get('/api/admin/stats/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_or_superuser_without_role_admin_is_still_forbidden(self):
        # role='admin' is this app's actual admin designation - is_staff/
        # is_superuser are Django's separate built-in flags and must NOT be
        # treated as equivalent (see core/permissions.py's own docstring).
        staff_user = CustomUser.objects.create_user(
            username='djangostaff', password='x', is_verified=True, is_staff=True, is_superuser=True,
        )
        self.client.force_authenticate(staff_user)
        resp = self.client.get('/api/admin/stats/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_role_user_is_allowed(self):
        admin = CustomUser.objects.create_user(username='realadmin', password='x', is_verified=True, role='admin')
        self.client.force_authenticate(admin)
        resp = self.client.get('/api/admin/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class AdminStatsViewTests(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(username='statsadmin', password='x', is_verified=True, role='admin')
        self.client.force_authenticate(self.admin)
        self.category = TravelCategory.objects.get_or_create(slug='beach', defaults={'name': 'Beach'})[0]

    def test_counts_reflect_real_seeded_data_not_hardcoded(self):
        CustomUser.objects.create_user(username='statsuser1', password='x', is_verified=True)
        CustomUser.objects.create_user(username='statsuser2', password='x', is_verified=True, is_active=False)
        dest = Destination.objects.create(
            name='Stat City', country='Testland', description='A place.',
            travel_type=self.category, estimated_cost=500, slug='stat-city',
        )
        Review.objects.create(user=self.admin, destination=dest, rating=4)

        resp = self.client.get('/api/admin/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # admin + statsuser1 (active) + statsuser2 (inactive) = 3 total
        self.assertEqual(resp.data['user_count'], 3)
        self.assertEqual(resp.data['inactive_user_count'], 1)
        self.assertEqual(resp.data['destination_count'], 1)
        self.assertEqual(resp.data['total_destination_reviews'], 1)
        self.assertEqual(resp.data['average_destination_rating'], 4.0)

    def test_most_searched_destinations_reflects_real_searchlog_rows(self):
        from destinations.models import SearchLog
        SearchLog.objects.create(query='paris', results_count=3)
        SearchLog.objects.create(query='paris', results_count=3)
        SearchLog.objects.create(query='tokyo', results_count=1)

        resp = self.client.get('/api/admin/stats/')
        top_query = resp.data['most_searched_destinations'][0]
        self.assertEqual(top_query['query'], 'paris')
        self.assertEqual(top_query['count'], 2)
