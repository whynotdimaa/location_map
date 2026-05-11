from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.locations.models import Location


class Review(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        # One review per user per location
        unique_together = ("location", "user")

    def __str__(self):
        return f"{self.user} → {self.location} ({self.rating}★)"

    @property
    def likes_count(self):
        return self.likes.filter(vote=ReviewLike.Vote.LIKE).count()

    @property
    def dislikes_count(self):
        return self.likes.filter(vote=ReviewLike.Vote.DISLIKE).count()


class ReviewLike(models.Model):
    class Vote(models.TextChoices):
        LIKE = "like", "Like"
        DISLIKE = "dislike", "Dislike"

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="review_likes")
    vote = models.CharField(max_length=10, choices=Vote.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "user")

    def __str__(self):
        return f"{self.user} {self.vote} → review#{self.review_id}"
