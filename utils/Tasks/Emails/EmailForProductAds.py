from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from utils.email_sender import send_custom_email
from utils.enum import GroupNames
from apps.aso.models import Product

User = get_user_model()

def send_new_product_announcement():
    """
    Notify all active customers that new products have been added.
    """
    users = (
        User.objects.filter(is_active=True, is_deleted=False, groups__name=GroupNames.CUSTOMER.value)
        .exclude(email__isnull=True)
        .exclude(email="")
    )

    new_products = Product.objects.filter(is_deleted=False, display_product=True).order_by("-created_at")[:5]
    product_names = [p.title for p in new_products]
    product_list = "\n".join(f"• {name}" for name in product_names)

    count = 0
    for user in users:
        send_custom_email(
            subject="New Arrivals: Discover What’s Fresh in Store!",
            recipient_email=user.email,
            message=f"""
            We’re thrilled to let you know that **new exclusive products** have just been added to our collection!  
            Each piece is carefully selected to bring you the best in quality, style, and craftsmanship.

            ✨ **Here’s a sneak peek:**  
            {product_list}

            🔗 Browse all new arrivals here: \n{settings.BASE_URL}/index.html

            Be among the first to explore and order these items are selling fast!  

            Thank you for being part of our community.  
            We can’t wait for you to experience what’s new at **Aso Oke & Aso Ofi**.
            """,
            greeting_name=user.first_name or "Valued Customer",
        )
        count += 1

    return f"✅ New product announcement sent to {count} users."
