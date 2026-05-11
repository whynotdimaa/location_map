from rest_framework import serializers

from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)

    class Meta:
        model = Subscription
        fields = ("id", "user", "location", "location_name", "created_at")
        read_only_fields = ("id", "user", "location_name", "created_at")

    def validate(self, attrs):
        user = self.context["request"].user
        location = attrs["location"]
        if Subscription.objects.filter(user=user, location=location).exists():
            raise serializers.ValidationError("Ви вже підписані на цю локацію.")
        return attrs
