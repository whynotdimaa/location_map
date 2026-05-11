from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from apps.locations.models import Location
from apps.reviews.models import Review


class ReviewFunctionalTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.location = Location.objects.create(
            user=self.user1, name="Кафе", latitude=50.0, longitude=30.0
        )
        # Додано префікс reviews:
        self.list_url = reverse('reviews:review-list')

    @patch('apps.reviews.tasks.notify_subscribers_on_new_review.delay')
    def test_create_review_updates_location_rating(self, mock_task):
        self.client.force_authenticate(user=self.user1)

        self.client.post(self.list_url, {
            "location": self.location.id, "comment": "Супер", "rating": 5
        })
        self.location.refresh_from_db()
        self.assertEqual(self.location.avg_rating, 5.0)
        mock_task.assert_called_once()

        self.client.force_authenticate(user=self.user2)
        self.client.post(self.list_url, {
            "location": self.location.id, "comment": "Норм", "rating": 3
        })
        self.location.refresh_from_db()
        self.assertEqual(self.location.avg_rating, 4.0)

    def test_cannot_create_multiple_reviews_per_location(self):
        self.client.force_authenticate(user=self.user1)
        data = {"location": self.location.id, "comment": "Текст", "rating": 4}

        self.client.post(self.list_url, data)
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_delete_review_recalculates_rating(self):
        self.client.force_authenticate(user=self.user1)
        review = Review.objects.create(location=self.location, user=self.user1, comment="Текст", rating=2)
        self.location.update_avg_rating()
        self.assertEqual(self.location.avg_rating, 2.0)

        # Додано префікс reviews:
        url = reverse('reviews:review-detail', kwargs={'pk': review.id})
        self.client.delete(url)
        self.location.refresh_from_db()
        self.assertEqual(self.location.avg_rating, 0.0)

    def test_review_voting(self):
        self.client.force_authenticate(user=self.user1)
        review = Review.objects.create(location=self.location, user=self.user2, comment="Текст", rating=4)
        vote_url = reverse('reviews:review-vote', kwargs={'pk': review.id})

        # Ставимо лайк
        response = self.client.post(vote_url, {"vote": "like"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(review.likes.count(), 1)

        # Знімаємо лайк (повторний запит)
        response = self.client.post(vote_url, {"vote": "like"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(review.likes.count(), 0)


