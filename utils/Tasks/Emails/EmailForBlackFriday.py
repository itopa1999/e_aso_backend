from datetime import timedelta
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from utils.decorators import checkBackgroundFeatureFlag
from utils.email_sender import send_custom_email
from utils.enum import FeatureNames, GroupNames
from utils.feature_flags import is_feature_enabled
from utils.telegram_helpers import send_announcement

User = get_user_model()

@checkBackgroundFeatureFlag()
@shared_task
def send_discount_day_announcement():
    """
    Send discount day email if the BLACK_FRIDAY feature flag is enabled.
    Uses the flag's actual end_date (DateTimeField) as the expiry time.
    """

    flag, enabled = is_feature_enabled(FeatureNames.BLACK_FRIDAY.value)
    if not enabled:
        return "⚠️ Discount day feature is disabled."

    if not flag.end_date:
        return "⚠️ No end date set for this discount feature."
    
    now = timezone.now()

    # Ensure the datetime is timezone-aware
    expiry_datetime = flag.end_date
    if timezone.is_naive(expiry_datetime):
        expiry_datetime = timezone.make_aware(expiry_datetime)

    # Check expiration
    if expiry_datetime < now:
        return f"⚠️ The discount feature expired on {expiry_datetime.strftime('%B %d, %Y at %I:%M %p')}."

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
            subject="Massive Discounts on All Products!",
            recipient_email=user.email,
            message=f"""
            Hey {user.first_name or "Valued Customer"},

            We're thrilled to announce that today is our Special Discount Day! 🎊

            For a limited time, every product in our store is discounted — no coupon needed.  
            Grab your favorites before time runs out!

            🛍️ What you get:
            • Exclusive discounts across all categories  
            • Offer valid until {expiry_datetime.strftime('%I:%M %p on %B %d, %Y')}

            Don't miss this chance to save big!  
            👉 Shop now: {settings.BASE_URL}/index.html

            Hurry! The clock is ticking ⏰
            """,
            greeting_name=user.first_name or "Valued Customer",
        )
        count += 1
        
    message = f"""
    Hey <b>Valued Customer</b>,  

    🎉 <b>Black Friday Discount Day is LIVE!</b> 🎉  

    For a <b>limited time</b>, every product in our store is discounted — no coupon needed!  
    Grab your favorites before time runs out.  

    🛍️ <b>What you get:</b>  
    • <b>Exclusive discounts</b> across all categories  
    • Offer valid until <b>{expiry_datetime.strftime('%I:%M %p on %B %d, %Y')}</b>  

    Don't miss this chance to <i>save big</i>!  
    👉 <b><a href="{settings.BASE_URL}/index.html">Shop now</a></b>  

    ⏰ <b>Hurry! The clock is ticking.</b>
    """
    send_announcement(message)
    
    return f"✅ Discount day email sent to {count} user(s). Offer ends {expiry_datetime.strftime('%I:%M %p on %B %d, %Y')}."
