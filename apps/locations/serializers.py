from rest_framework import serializers

from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Location
        fields = (
            "id", "user", "name", "description", "category",
            "latitude", "longitude", "avg_rating", "created_at", "updated_at",
        )
        read_only_fields = ("id", "user", "avg_rating", "created_at", "updated_at")

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Широта повинна бути між -90 і 90.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Довгота повинна бути між -180 і 180.")
        return value


class LocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Location
        fields = ("id", "user", "name", "category", "avg_rating", "latitude", "longitude")
