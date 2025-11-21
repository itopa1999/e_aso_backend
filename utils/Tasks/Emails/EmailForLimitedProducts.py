from datetime import timedelta
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from utils.decorators import checkBackgroundFeatureFlag
from utils.email_sender import send_custom_email
from utils.enum import FeatureNames, GroupNames
from utils.feature_flags import is_feature_enabled

User = get_user_model()


@checkBackgroundFeatureFlag()
@shared_task
def send_limited_day_announcement():
    """
    Send limited day email if the Limited feature flag is enabled.
    Uses the flag's actual end_date (DateTimeField) as the expiry time.
    """

    flag, enabled = is_feature_enabled(FeatureNames.PRODUCT_LIMITATION.value)
    if not enabled or not flag:
        return "⚠️ Limited day feature is disabled."

    if not flag.end_date:
        return "⚠️ No end date set for this limited feature."
    
    now = timezone.now()

    # Ensure the datetime is timezone-aware
    expiry_datetime = flag.end_date
    if timezone.is_naive(expiry_datetime):
        expiry_datetime = timezone.make_aware(expiry_datetime)

    # Check expiration
    if expiry_datetime < now:
        return f"⚠️ The limited feature expired on {expiry_datetime.strftime('%B %d, %Y at %I:%M %p')}."

    # Get active customer users
    users = (
        User.objects.filter(
            is_active=True,
            is_deleted=False,
            groups__name=GroupNames.CUSTOMER.value
        )
        .exclude(email__isnull=True)
        .exclude(email="")
    )

    count = 0
    for user in users:
        send_custom_email(
            subject="Limited Products Now Available: Shop Today!",
            recipient_email=user.email,
            message=f"""
            Hey {user.first_name or "Valued Customer"},

            We are excited to inform you that our Limited Product Collection is now available.  
            Take advantage of exclusive discounts for a limited time.

            Offer Details:
            • Discounts applied automatically to selected products  
            • Offer valid until {expiry_datetime.strftime('%I:%M %p on %B %d, %Y')}

            🛍️ What you get:
            • Exclusive discounts across all categories  
            • Offer valid until {expiry_datetime.strftime('%I:%M %p on %B %d, %Y')}

            Visit our store now to secure your favorite items: {settings.BASE_URL}/limited-products.html

            """,
            greeting_name=user.first_name or "Valued Customer",
        )
        count += 1

    return f"✅ Limited product email sent to {count} user(s). Offer ends {expiry_datetime.strftime('%I:%M %p on %B %d, %Y')}."
