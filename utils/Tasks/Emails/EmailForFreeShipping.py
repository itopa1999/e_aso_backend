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
def send_free_shipping_announcement():
    """
    Notify all users that free shipping is available for a limited time.
    """
    
    flag, enable = is_feature_enabled(FeatureNames.FREE_DELIVERY.value)
    if not enable:
        return "Free shipping feature is disabled."
    
    if not flag.end_date:
        return "⚠️ No end date set for free shipping feature."
    
    if flag.is_active:
        return "⚠️ Free shipping is already active."
    
    now = timezone.now()

    # Ensure the datetime is timezone-aware
    expiry_datetime = flag.end_date
    if timezone.is_naive(expiry_datetime):
        expiry_datetime = timezone.make_aware(expiry_datetime)

    # Check expiration
    if expiry_datetime < now:
        return f"⚠️ The free shipping feature expired on {expiry_datetime.strftime('%B %d, %Y at %I:%M %p')}."

    users = User.objects.filter(is_active=True, is_deleted=False, groups__name=GroupNames.CUSTOMER.value).exclude(email__isnull=True).exclude(email="")
    count = 0
    for user in users:
        send_custom_email(
            subject="Free Shipping Alert: Limited Time Offer!",
            recipient_email=user.email,
            message=f"""
            Good news! We're offering FREE SHIPPING on all orders placed before  
            🕓 {expiry_datetime.strftime('%I:%M %p on %B %d, %Y')}.

            Don't wait — fill your cart and check out now to enjoy this limited-time offer!  

            👉 Visit our store to start shopping: {settings.BASE_URL}/index.html

            """,
            greeting_name=user.first_name or "Valued Customer",
        )
        count += 1
        
    flag.is_active = True
    flag.save(update_fields=['is_active'])
    
    message = f"""
    🎉 <b>FREE SHIPPING ALERT!</b> 🎉

    Hey shoppers! We're excited to announce that <b>FREE SHIPPING</b> is available on all orders for a limited time.  

    🕓 Offer ends at <b>{expiry_datetime.strftime('%I:%M %p on %B %d, %Y')}</b> — don’t miss out!  

    Fill your cart and enjoy this exclusive benefit today.  

    👉 <b><a href="{settings.BASE_URL}/index.html">Shop Now</a></b>

    Happy shopping! 🛍️
    """
    send_announcement(message)

    return f"✅ Free shipping email sent to {count} user(s)."
