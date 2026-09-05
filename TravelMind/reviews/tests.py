from rest_framework.test import APITestCase
from rest_framework import status

from destinations.models import Destination, TravelCategory
from users.models import CustomUser
from .models import Review, AppReview


def make_destination(**overrides):
    category, _ = TravelCategory.objects.get_or_create(slug='beach', defaults={'name': 'Beach'})
    defaults = {
        'name': 'Test City', 'country': 'Testland', 'description': 'A place.',
        'travel_type': category, 'estimated_cost': 500, 'slug': 'test-city',
    }
    defaults.update(overrides)
    return Destination.objects.create(**defaults)


class DestinationReviewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='reviewer', password='x', is_verified=True)
        self.destination = make_destination()
        self.client.force_authenticate(self.user)

    def test_create_review_assigns_current_user(self):
        resp = self.client.post(f'/api/reviews/{self.destination.id}/', {'rating': 5, 'comment': 'Great!'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['username'], 'reviewer')
        review = Review.objects.get(pk=resp.data['id'])
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.destination, self.destination)

    def test_cannot_review_same_destination_twice(self):
        Review.objects.create(user=self.user, destination=self.destination, rating=4)
        resp = self.client.post(f'/api/reviews/{self.destination.id}/', {'rating': 3, 'comment': 'Again'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.filter(user=self.user, destination=self.destination).count(), 1)

    def test_different_users_can_each_review_same_destination(self):
        other = CustomUser.objects.create_user(username='reviewer2', password='x', is_verified=True)
        Review.objects.create(user=self.user, destination=self.destination, rating=4)

        self.client.force_authenticate(other)
        resp = self.client.post(f'/api/reviews/{self.destination.id}/', {'rating': 2, 'comment': 'Meh'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.filter(destination=self.destination).count(), 2)

    def test_rating_out_of_bounds_is_rejected(self):
        resp = self.client.post(f'/api/reviews/{self.destination.id}/', {'rating': 6, 'comment': 'Too high'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_for_nonexistent_destination_returns_404_not_500(self):
        resp = self.client.post('/api/reviews/999999/', {'rating': 5, 'comment': 'Nowhere'})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_reviews_requires_authentication(self):
        self.client.force_authenticate(None)
        resp = self.client.get(f'/api/reviews/{self.destination.id}/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class AppReviewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='appreviewer', password='x', is_verified=True)
        self.client.force_authenticate(self.user)

    def test_create_and_fetch_own_app_review(self):
        resp = self.client.post('/api/reviews/app/me/', {'rating': 5, 'comment': 'Love it'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        get_resp = self.client.get('/api/reviews/app/me/')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.data['rating'], 5)

    def test_cannot_submit_a_second_app_review(self):
        AppReview.objects.create(user=self.user, rating=4, comment='First')
        resp = self.client.post('/api/reviews/app/me/', {'rating': 5, 'comment': 'Second'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AppReview.objects.filter(user=self.user).count(), 1)

    def test_can_edit_own_app_review(self):
        AppReview.objects.create(user=self.user, rating=3, comment='Meh')
        resp = self.client.put('/api/reviews/app/me/', {'rating': 5, 'comment': 'Actually great'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['rating'], 5)

    def test_get_own_review_when_none_exists_returns_null_not_404(self):
        resp = self.client.get('/api/reviews/app/me/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(resp.data)

    def test_app_review_list_reports_real_average(self):
        other = CustomUser.objects.create_user(username='appreviewer2', password='x', is_verified=True)
        AppReview.objects.create(user=self.user, rating=4, comment='Good')
        AppReview.objects.create(user=other, rating=2, comment='Meh')

        resp = self.client.get('/api/reviews/app/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['total_reviews'], 2)
        self.assertEqual(resp.data['average_rating'], 3.0)
