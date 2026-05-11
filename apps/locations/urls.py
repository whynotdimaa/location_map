from rest_framework.routers import SimpleRouter

from .views import LocationViewSet

router = SimpleRouter()
router.register("", LocationViewSet, basename="location")

urlpatterns = router.urls
