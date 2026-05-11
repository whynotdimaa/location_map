from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from apps.locations.models import Location
from apps.locations.views import LOCATIONS_CACHE_KEY

class LocationFunctionalTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="owner", password="password123")
        self.client.force_authenticate(user=self.user)
        # Додано префікс locations:
        self.list_url = reverse('locations:location-list')

    def test_create_location_success(self):
        data = {
            "name": "Парк Шевченка",
            "category": "park",
            "latitude": 50.4419,
            "longitude": 30.5136
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Location.objects.first().user, self.user)

    def test_invalid_coordinates(self):
        data = {
            "name": "Погана Локація",
            "latitude": 100.0,
            "longitude": 200.0
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('latitude', response.data)
        self.assertIn('longitude', response.data)

    def test_cache_invalidation_on_create(self):
        self.client.get(self.list_url)
        self.assertIsNotNone(cache.get(LOCATIONS_CACHE_KEY))

        data = {"name": "Нова", "latitude": 50.0, "longitude": 30.0}
        self.client.post(self.list_url, data)

        self.assertIsNone(cache.get(LOCATIONS_CACHE_KEY))

    def test_location_filtering(self):
        # Створюємо дві різні локації
        Location.objects.create(user=self.user, name="Музей води", category="museum", latitude=50.1, longitude=30.1)
        Location.objects.create(user=self.user, name="Кафе Смак", category="cafe", latitude=50.2, longitude=30.2)

        # Перевіряємо фільтр за категорією
        response = self.client.get(self.list_url + '?category=museum')
        self.assertEqual(len(response.data['results'] if 'results' in response.data else response.data), 1)
        self.assertEqual((response.data['results'][0] if 'results' in response.data else response.data[0])['name'],
                         "Музей води")

    def test_export_csv(self):
        # Спочатку створюємо локацію, щоб було що експортувати
        Location.objects.create(user=self.user, name="Тест", latitude=50.0, longitude=30.0)

        response = self.client.get('/api/locations/export/?export_format=csv')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="locations.csv"', response['Content-Disposition'])

    def test_export_json(self):
        response = self.client.get('/api/locations/export/?export_format=json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)