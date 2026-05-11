from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from apps.locations.models import Location
from apps.subscriptions.models import Subscription


class SubscriptionFunctionalTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="sub_user", password="password123")
        self.location = Location.objects.create(
            user=self.user, name="Музей", latitude=50.0, longitude=30.0
        )
        self.client.force_authenticate(user=self.user)
        # Використовуємо прямий шлях до API
        self.url = '/api/subscriptions/'

    def test_subscribe_to_location(self):
        response = self.client.post(self.url, {"location": self.location.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)

    def test_cannot_subscribe_twice(self):
        Subscription.objects.create(user=self.user, location=self.location)
        response = self.client.post(self.url, {"location": self.location.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_unsubscribe(self):
        sub = Subscription.objects.create(user=self.user, location=self.location)
        # Прямий шлях для видалення конкретної підписки
        delete_url = f'/api/subscriptions/{sub.id}/'

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subscription.objects.count(), 0)