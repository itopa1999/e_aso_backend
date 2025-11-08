from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from utils.email_sender import send_custom_email
from utils.enum import FeatureNames, GroupNames
from utils.feature_flags import is_feature_enabled

User = get_user_model()

def send_discount_day_announcement(hours_valid=12):
    """
    Notify all users that today is a discount-free day (limited time discount on all products).
    
    Args:
        hours_valid (int): Number of hours the promo lasts (default = 12).
    """
    flag, enable = is_feature_enabled(FeatureNames.BLACK_FRIDAY.value)
    if not enable:
        return "Discount day feature is disabled."
    
    expiry_time = timezone.now() + timedelta(hours=hours_valid)

    users = (
        User.objects.filter(is_active=True, is_deleted=False, groups__name=GroupNames.CUSTOMER.value)
        .exclude(email__isnull=True)
        .exclude(email="")
    )

    count = 0
    for user in users:
        send_custom_email(
            subject="Today Only: Enjoy Massive Discounts on All Products!",
            recipient_email=user.email,
            message=f"""
            We’re excited to announce that **today is our Special Discount Day!** 🎊

            For a limited time, **every product in our store is discounted** no coupon needed.  
            This is your chance to grab your favorite items at unbeatable prices.

            🛍️ What you get:
            - Exclusive discounts across all categories  
            - Offer valid until 🕓 {expiry_time.strftime('%I:%M %p on %B %d, %Y')}

            Don’t miss out on this limited-time opportunity to save big!  
            👉 Visit our store and start shopping now: \n{settings.BASE_URL}/index.html

            Hurry! The clock is ticking ⏰

            """,
            greeting_name=user.first_name or "Valued Customer",
        )
        count += 1

    return f"✅ Discount day email sent to {count} user(s)."
