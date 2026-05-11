from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import LocationViewSet

app_name = "locations"

router = SimpleRouter()
router.register("", LocationViewSet, basename="location")

urlpatterns = router.urls
