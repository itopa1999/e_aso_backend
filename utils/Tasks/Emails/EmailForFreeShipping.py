from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from utils.email_sender import send_custom_email
from utils.enum import FeatureNames, GroupNames
from utils.feature_flags import is_feature_enabled

User = get_user_model()

def send_free_shipping_announcement(hours_valid=6):
    """
    Notify all users that free shipping is available for a limited time.
    
    Args:
        hours_valid (int): Number of hours the promo lasts (default = 6).
    """
    flag, enable = is_feature_enabled(FeatureNames.FREE_DELIVERY.value)
    if not enable:
        return "Free shipping feature is disabled."
    expiry_time = timezone.now() + timedelta(hours=hours_valid)

    users = User.objects.filter(is_active=True, is_deleted=False, groups__name=GroupNames.CUSTOMER.value).exclude(email__isnull=True).exclude(email="")
    count = 0
    for user in users:
        send_custom_email(
            subject="Free Shipping Alert: Limited Time Offer!",
            recipient_email=user.email,
            message=f"""
            Good news! We’re offering **FREE SHIPPING** on all orders placed before  
            🕓 {expiry_time.strftime('%I:%M %p on %B %d, %Y')}.

            Don’t wait — fill your cart and check out now to enjoy this limited-time offer!  

            👉 Visit your store to start shopping: \n{settings.BASE_URL}/index.html

            """,
            greeting_name=user.first_name or "Valued Customer",
        )
        count += 1

    return f"✅ Free shipping email sent to {count} user(s)."
