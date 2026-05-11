from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import ModelViewSet

from .models import Review, ReviewLike
from .serializers import ReviewLikeSerializer, ReviewSerializer
from .tasks import notify_subscribers_on_new_review


class ReviewCreateThrottle(UserRateThrottle):
    rate = "10/hour"


class VoteThrottle(UserRateThrottle):
    rate = "60/hour"


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.select_related("user", "location").all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_fields = ("location",)
    ordering_fields = ("created_at", "rating")
    ordering = ("-created_at",)

    def get_throttles(self):
        if self.action == "create":
            return [ReviewCreateThrottle()]
        elif self.action == "vote":
            return [VoteThrottle()]
        return super().get_throttles()

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        review.location.update_avg_rating()
        notify_subscribers_on_new_review.delay(review.id)

    def perform_update(self, serializer):
        review = serializer.save()
        review.location.update_avg_rating()

    def perform_destroy(self, instance):
        location = instance.location
        instance.delete()
        location.update_avg_rating()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        """Like or dislike a review. Sending the same vote again removes it."""
        review = self.get_object()
        serializer = ReviewLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vote_value = serializer.validated_data["vote"]
        existing = ReviewLike.objects.filter(review=review, user=request.user).first()

        if existing:
            if existing.vote == vote_value:
                existing.delete()
                return Response({"detail": "Голос знятий."}, status=status.HTTP_200_OK)
            existing.vote = vote_value
            existing.save(update_fields=["vote"])
            return Response({"detail": "Голос змінено."}, status=status.HTTP_200_OK)

        ReviewLike.objects.create(review=review, user=request.user, vote=vote_value)
        return Response({"detail": "Голос зараховано."}, status=status.HTTP_201_CREATED)
