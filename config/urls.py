from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/locations/", include("apps.locations.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/subscriptions/", include("apps.subscriptions.urls")),
]
