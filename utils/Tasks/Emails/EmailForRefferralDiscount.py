from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from utils.decorators import checkBackgroundFeatureFlag
from utils.email_sender import send_custom_email
from utils.enum import FeatureNames, GroupNames
from utils.feature_flags import is_feature_enabled
from utils.telegram_helpers import send_announcement

User = get_user_model()


@checkBackgroundFeatureFlag()
@shared_task
def send_referral_program_announcement():
    """
    Send an email to all customers announcing that the referral program is live.
    Encourage them to share their referral code and earn a discount once their friend completes a purchase.
    """
    flag, enable = is_feature_enabled(FeatureNames.REFERRAL_SYSTEM.value)
    if not enable:
        return "Referral system feature is disabled."
    
    if flag.is_active:
        return "⚠️ Referral program is already active."

    users = (
        User.objects.filter(
            is_active=True,
            is_deleted=False,
            groups__name=GroupNames.CUSTOMER.value
        )
        .exclude(email__isnull=True)
        .exclude(email="")
        .distinct()
    )

    count = 0
    for user in users:
        send_custom_email(
            subject="Refer & Earn: Get Discounts When Your Friends Shop!",
            recipient_email=user.email,
            message=f"""
            Great news! Our Referral Program is now live on Aso Oke & Aso Ofi Marketplace.  

            You can now earn exclusive shopping discounts when your friends use your referral code and complete their purchase.

            Here's how it works:
            • 💬 Share your unique referral code with friends and family  
            • 🛍️ When they buy using your code, you'll automatically receive a discount for your next order  
            • 🎁 The more completed purchases from your referrals, the more rewards you earn!

            It's that simple! Invite, shop, and save.  

            👉 View and share your referral code here: {settings.BASE_URL}/profile.html

            Don't miss out — start inviting friends today and enjoy amazing discounts once their orders are completed!
            """,
            greeting_name=user.first_name or "Valued Customer",
        )
        count += 1
        
    flag.is_active = True
    flag.save(update_fields=['is_active'])
    
    
    message = f"""
    🎉 <b>Referral Program is LIVE!</b> 🎉

    Hey shoppers! You can now <b>earn exclusive discounts</b> by inviting your friends to shop at Aso Oke & Aso Ofi Marketplace.  

    How it works:  
    • 💬 Share your unique referral code with friends and family  
    • 🛍️ When they shop using your code, you get a discount on your next order  
    • 🎁 The more friends complete purchases, the more rewards you earn!  

    It's that simple! Invite, shop, and save.  

    👉 <b><a href="{settings.BASE_URL}/profile.html">View & Share Your Referral Code</a></b>  

    Don't wait — start referring today and enjoy amazing discounts! 🛒
    """

    send_announcement(message)

    return f"✅ Referral program announcement sent to {count} user(s)."
