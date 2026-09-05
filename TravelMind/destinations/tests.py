from rest_framework.test import APITestCase
from rest_framework import status
from django.db.models import Avg, Count

from users.models import CustomUser
from reviews.models import Review
from .models import Destination, TravelCategory, Season
from .serializers import DestinationSerializer


def make_category(slug, name=None):
    return TravelCategory.objects.get_or_create(slug=slug, defaults={'name': name or slug.title()})[0]


def make_season(slug, name=None):
    return Season.objects.get_or_create(slug=slug, defaults={'name': name or slug.title()})[0]


def make_destination(**overrides):
    category = overrides.pop('travel_type', None) or make_category('beach', 'Beach')
    defaults = {
        'name': 'Test City', 'country': 'Testland', 'description': 'A place.',
        'travel_type': category, 'estimated_cost': 500, 'slug': 'test-city',
    }
    defaults.update(overrides)
    return Destination.objects.create(**defaults)


class DestinationListFilterTests(APITestCase):
    def setUp(self):
        self.beach = make_category('beach', 'Beach')
        self.mountain = make_category('mountain', 'Mountain')
        self.user = CustomUser.objects.create_user(username='browser', password='x', is_verified=True)
        self.client.force_authenticate(self.user)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        resp = self.client.get('/api/destinations/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_travel_type_slug(self):
        make_destination(slug='beach-1', name='Beach One', travel_type=self.beach)
        make_destination(slug='mountain-1', name='Mountain One', travel_type=self.mountain)

        resp = self.client.get('/api/destinations/', {'travel_type': 'beach'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [d['name'] for d in resp.data['results']]
        self.assertIn('Beach One', names)
        self.assertNotIn('Mountain One', names)

    def test_filter_by_budget_range(self):
        make_destination(slug='cheap', name='Cheap Place', estimated_cost=100, travel_type=self.beach)
        make_destination(slug='pricey', name='Pricey Place', estimated_cost=5000, travel_type=self.beach)

        resp = self.client.get('/api/destinations/', {'budget_max': 1000})
        names = [d['name'] for d in resp.data['results']]
        self.assertIn('Cheap Place', names)
        self.assertNotIn('Pricey Place', names)

    def test_filter_by_country_matches_macedonian_field_too(self):
        make_destination(slug='de', name='Berlin', country='Germany', country_mk='Германија', travel_type=self.beach)
        resp = self.client.get('/api/destinations/', {'country': 'Герман'})
        names = [d['name'] for d in resp.data['results']]
        self.assertIn('Berlin', names)


class SlugGenerationTests(APITestCase):
    def setUp(self):
        self.beach = make_category('beach4', 'Beach')
        self.admin = CustomUser.objects.create_user(
            username='destadmin', password='x', role='admin', is_verified=True,
        )
        self.client.force_authenticate(self.admin)

    def test_slug_is_derived_from_name_when_omitted(self):
        resp = self.client.post('/api/destinations/admin/create/', {
            'name': 'Sunny Beach', 'country': 'Testland', 'description': 'Nice.',
            'travel_type': self.beach.slug, 'estimated_cost': 400,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['slug'], 'sunny-beach')

    def test_slug_collision_gets_deduplicated(self):
        make_destination(slug='sunny-beach', name='Existing', travel_type=self.beach)

        resp = self.client.post('/api/destinations/admin/create/', {
            'name': 'Sunny Beach', 'country': 'Testland', 'description': 'Nice.',
            'travel_type': self.beach.slug, 'estimated_cost': 400,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['slug'], 'sunny-beach-2')

    def test_non_admin_cannot_create_destination(self):
        regular = CustomUser.objects.create_user(username='regularjoe', password='x', is_verified=True)
        self.client.force_authenticate(regular)
        resp = self.client.post('/api/destinations/admin/create/', {
            'name': 'Nope', 'country': 'Testland', 'description': 'Nice.',
            'travel_type': self.beach.slug, 'estimated_cost': 400,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class RatingAnnotationTests(APITestCase):
    """average_rating/review_count must reflect real Review rows, computed
    the same way whether the queryset was pre-annotated (list/detail views)
    or not (the SerializerMethodField's fallback path)."""

    def setUp(self):
        self.beach = make_category('beach5', 'Beach')
        self.user = CustomUser.objects.create_user(username='rater', password='x', is_verified=True)
        self.other = CustomUser.objects.create_user(username='rater2', password='x', is_verified=True)
        self.client.force_authenticate(self.user)

    def test_average_rating_and_review_count_reflect_real_reviews(self):
        dest = make_destination(slug='rated-dest', name='Rated Place', travel_type=self.beach)
        Review.objects.create(user=self.user, destination=dest, rating=4)
        Review.objects.create(user=self.other, destination=dest, rating=2)

        resp = self.client.get(f'/api/destinations/{dest.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['review_count'], 2)
        self.assertEqual(resp.data['average_rating'], 3.0)

    def test_no_reviews_means_null_average_and_zero_count(self):
        dest = make_destination(slug='unrated-dest', name='Unrated Place', travel_type=self.beach)
        resp = self.client.get(f'/api/destinations/{dest.id}/')
        self.assertIsNone(resp.data['average_rating'])
        self.assertEqual(resp.data['review_count'], 0)

    def test_zero_review_destinations_use_the_annotated_fast_path_not_a_per_object_query(self):
        # Regression test: Avg('reviews__rating') annotates to None for a
        # destination with zero reviews (SQL AVG of an empty group is NULL) -
        # that's a legitimate annotated result, not "unannotated". A naive
        # "annotated value is not None" check would silently fall through to
        # a per-object reviews.exists() query for every such destination,
        # defeating the whole point of the annotation (found via
        # assertNumQueries on a list of unrated destinations).
        for i in range(5):
            make_destination(slug=f'unrated-{i}', name=f'Unrated {i}', travel_type=self.beach)

        with self.assertNumQueries(1):
            list(DestinationSerializer(
                Destination.objects.select_related('travel_type', 'best_season').annotate(
                    avg_rating_annotated=Avg('reviews__rating'),
                    review_count_annotated=Count('reviews', distinct=True),
                ),
                many=True, context={'request': None},
            ).data)


class TaxonomyProtectedDeleteTests(APITestCase):
    """Deleting a TravelCategory/Season still referenced by a destination
    must return a clean 400 with a helpful message, not an opaque 500 from
    the underlying on_delete=PROTECT constraint."""

    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            username='taxadmin', password='x', role='admin', is_verified=True,
        )
        self.client.force_authenticate(self.admin)

    def test_deleting_in_use_category_returns_clean_400(self):
        category = make_category('in-use', 'In Use')
        make_destination(slug='uses-category', name='Uses It', travel_type=category)

        resp = self.client.delete(f'/api/destinations/admin/categories/{category.id}/')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', resp.data)
        self.assertTrue(TravelCategory.objects.filter(pk=category.pk).exists())

    def test_deleting_unused_category_succeeds(self):
        category = make_category('unused', 'Unused')
        resp = self.client.delete(f'/api/destinations/admin/categories/{category.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TravelCategory.objects.filter(pk=category.pk).exists())

    def test_deleting_in_use_season_returns_clean_400(self):
        season = make_season('in-use-season', 'In Use Season')
        make_destination(slug='uses-season', name='Uses Season', best_season=season, travel_type=make_category('beach6'))

        resp = self.client.delete(f'/api/destinations/admin/seasons/{season.id}/')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', resp.data)
