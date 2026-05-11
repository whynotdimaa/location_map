import csv
import io

import pandas as pd
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import LocationFilter
from .models import Location
from .serializers import LocationListSerializer, LocationSerializer

LOCATIONS_CACHE_KEY = "locations:list"
LOCATION_CACHE_TTL = 60 * 15  # 15 minutes


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.select_related("user").all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_class = LocationFilter
    search_fields = ("name", "description")
    ordering_fields = ("avg_rating", "created_at")
    ordering = ("-created_at",)

    def get_serializer_class(self):
        if self.action == "list":
            return LocationListSerializer
        return LocationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        cache.delete(LOCATIONS_CACHE_KEY)

    def perform_update(self, serializer):
        serializer.save()
        cache.delete(LOCATIONS_CACHE_KEY)

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(LOCATIONS_CACHE_KEY)

    def list(self, request, *args, **kwargs):
        # Only cache unfiltered, unpaginated requests
        if not request.query_params:
            cached = cache.get(LOCATIONS_CACHE_KEY)
            if cached:
                return Response(cached)

        response = super().list(request, *args, **kwargs)

        if not request.query_params:
            cache.set(LOCATIONS_CACHE_KEY, response.data, LOCATION_CACHE_TTL)

        return response

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def export(self, request):
        fmt = request.query_params.get("format", "json")
        locations = self.filter_queryset(self.get_queryset())
        serializer = LocationSerializer(locations, many=True)
        data = serializer.data

        if fmt == "csv":
            df = pd.DataFrame(data)
            output = io.StringIO()
            df.to_csv(output, index=False)
            response = HttpResponse(output.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="locations.csv"'
            return response

        return Response(data)
