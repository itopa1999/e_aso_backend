from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from apps.aso.models import Cart
from utils.email_sender import send_custom_email


def send_abandoned_cart_reminders():
    """Send email reminders for carts inactive for 2 days."""
    threshold = timezone.now() - timedelta(minutes=2)

    # Filter carts that have items and haven’t been updated recently
    carts = (
        Cart.objects.filter(is_deleted=False, items__isnull=False)
        .filter(modified_at__lt=threshold)
        .distinct()
    )

    for cart in carts:
        user = cart.user
        
        item_count = cart.items.count()
        

        # Send reminder email
        send_custom_email(
            subject="You left items in your cart: Complete your purchase!",
            recipient_email=user.email,
            message=f"""
            You have {item_count} item(s) waiting in your cart.  
            Don't miss out — complete your purchase today!

            👉 Visit your cart to continue shopping: {settings.BASE_URL}/cart-item.html

            """,
            greeting_name=user.first_name or "Valued Customer",
        )

    return f"Sent reminders for {carts.count()} abandoned cart(s)."
