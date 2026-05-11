from django.urls import path

from .views import SubscriptionDetailView, SubscriptionView

urlpatterns = [
    path("", SubscriptionView.as_view(), name="subscriptions"),
    path("<int:pk>/", SubscriptionDetailView.as_view(), name="subscription-detail"),
]
