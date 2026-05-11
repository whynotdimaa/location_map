from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import ReviewViewSet

router = SimpleRouter()
router.register("", ReviewViewSet, basename="review")

# Manually add custom action routes
urlpatterns = router.urls + [
    path("<int:pk>/vote/", ReviewViewSet.as_view({"post": "vote"}), name="review-vote"),
]
