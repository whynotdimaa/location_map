from django.urls import path

from .views import SubscriptionDetailView, SubscriptionView

app_name = "subscriptions"

urlpatterns = [
    path("", SubscriptionView.as_view(), name="subscription-list"),
    path("<int:pk>/", SubscriptionDetailView.as_view(), name="subscription-detail"),
]
