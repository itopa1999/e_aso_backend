from celery import shared_task
from backend import settings
from utils.decorators import checkBackgroundFeatureFlag
from django.contrib.auth import get_user_model

from utils.email_sender import send_custom_email
from utils.enum import FeatureNames, GroupNames
from utils.feature_flags import is_feature_enabled
from utils.telegram_helpers import send_announcement


User = get_user_model()


@checkBackgroundFeatureFlag()
@shared_task
def send_feedback_email_announcement():
    """
    Send an email to all customers requesting feedback about their shopping experience.
    Encourages customers to rate and review products they purchased.
    """
    flag, enable = is_feature_enabled(FeatureNames.FEEDBACK.value)
    if not enable:
        return "Feedback feature is disabled."
    
    if flag.is_active:
        return "⚠️ Feedback campaign is already active."

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
            subject="Your Feedback Matters: Share Your Experience at Aso Oke & Aso Ofi",
            recipient_email=user.email,
            message=f"""
We hope you've had a wonderful shopping experience with Aso Oke & Aso Ofi Marketplace!

Your feedback is invaluable in helping us maintain the highest quality of service and products. We'd love to hear about your recent purchase experience, including:

✨ What You Can Share:
• Product quality and description accuracy
• Shipping and delivery experience
• Customer service experience
• Suggestions for improvement
• Product ratings (1-5 stars)

🌟 Why Your Feedback Matters:
• Helps us improve our products and services
• Assists other customers in making informed decisions
• Shows us what we're doing well and where we can improve
• Your voice shapes the future of our marketplace

📝 How to Leave Feedback:
Simply log in to your account and visit our feedback section to share your thoughts. It typically takes just 2-3 minutes, and your insights are greatly appreciated.

👉 Leave Your Feedback: {settings.BASE_URL}/feedback-page.html

Thank you for choosing Aso Oke & Aso Ofi Marketplace. We truly value your business and your feedback!

Warm regards,
The Aso Oke & Aso Ofi Team
            """,
            greeting_name=user.first_name or "Valued Customer",
        )
        count += 1
        
    flag.is_active = True
    flag.save(update_fields=['is_active'])
    
    message = f"""
🌟 <b>We Value Your Feedback!</b> 🌟

Dear Valued Customer,

Your shopping experience matters to us! We'd love to hear your thoughts about your recent purchase at <b>Aso Oke & Aso Ofi Marketplace</b>.

📝 <b>Share Your Experience:</b>
• Rate the products you purchased (1-5 stars)
• Tell us about the quality and accuracy of product descriptions
• Share your delivery and customer service experience
• Let us know how we can serve you better

Your feedback helps us:
✓ Improve product quality and selection
✓ Enhance our services
✓ Help other customers make informed choices
✓ Build a better marketplace for everyone

<b>Leave Your Feedback Now:</b>
👉 <a href="{settings.BASE_URL}/feedback-page.html"><b>Share Your Thoughts</b></a>

It takes just 2-3 minutes, and your voice truly matters!

Thank you for being part of our community.

<b>The Aso Oke & Aso Ofi Team</b>
    """

    send_announcement(message)

    return f"✅ Feedback request email sent to {count} user(s)."
