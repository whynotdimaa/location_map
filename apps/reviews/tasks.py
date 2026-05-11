from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def notify_subscribers_on_new_review(review_id: int) -> None:
    """Send email to all subscribers of a location when a new review is posted."""
    from apps.reviews.models import Review
    from apps.subscriptions.models import Subscription

    try:
        review = Review.objects.select_related("user", "location").get(id=review_id)
    except Review.DoesNotExist:
        return

    subscribers = Subscription.objects.filter(
        location=review.location
    ).exclude(
        user=review.user
    ).select_related("user")

    emails = [sub.user.email for sub in subscribers if sub.user.email]
    if not emails:
        return

    subject = f"Новий відгук для «{review.location.name}»"
    message = (
        f"Користувач {review.user.username} залишив відгук:\n\n"
        f"{review.comment}\n\n"
        f"Оцінка: {review.rating}/5"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=True,
    )
