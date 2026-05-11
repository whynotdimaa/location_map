from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import LocationViewSet

router = SimpleRouter()
router.register("", LocationViewSet, basename="location")

urlpatterns = [
    path("export/", LocationViewSet.as_view({"get": "export"}), name="location-export"),
] + router.urls
