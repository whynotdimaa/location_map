from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription
from .serializers import SubscriptionSerializer


class SubscriptionView(APIView):
    """
    GET  /api/subscriptions/        — list user's subscriptions
    POST /api/subscriptions/        — subscribe to a location
    DELETE /api/subscriptions/<id>/ — unsubscribe
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        subs = Subscription.objects.filter(user=request.user).select_related("location")
        serializer = SubscriptionSerializer(subs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubscriptionDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            sub = Subscription.objects.get(pk=pk, user=request.user)
        except Subscription.DoesNotExist:
            return Response({"detail": "Підписку не знайдено."}, status=status.HTTP_404_NOT_FOUND)
        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
