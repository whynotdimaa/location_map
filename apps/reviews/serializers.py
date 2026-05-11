from rest_framework import serializers

from .models import Review, ReviewLike


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Review
        fields = (
            "id", "user", "location", "comment", "rating",
            "likes_count", "dislikes_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "user", "likes_count", "dislikes_count", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context["request"]
        location = attrs.get("location")
        if self.instance is None:
            if Review.objects.filter(user=request.user, location=location).exists():
                raise serializers.ValidationError("Ви вже залишали відгук для цієї локації.")
        return attrs


class ReviewLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLike
        fields = ("id", "vote")
