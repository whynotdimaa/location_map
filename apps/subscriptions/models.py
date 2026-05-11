from django.contrib.auth.models import User
from django.db import models

from apps.locations.models import Location


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="subscriptions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "location")

    def __str__(self):
        return f"{self.user} → {self.location}"
