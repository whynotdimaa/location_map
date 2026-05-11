from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.TextChoices):
    RESTAURANT = "restaurant", "Ресторан"
    PARK = "park", "Парк"
    MUSEUM = "museum", "Музей"
    CAFE = "cafe", "Кафе"
    HOTEL = "hotel", "Готель"
    ATTRACTION = "attraction", "Атракція"
    OTHER = "other", "Інше"


class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.OTHER)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=500, blank=True)
    avg_rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name

    def update_avg_rating(self):
        from apps.reviews.models import Review
        result = self.reviews.aggregate(avg=models.Avg("rating"))
        self.avg_rating = result["avg"] or 0.0
        self.save(update_fields=["avg_rating"])
