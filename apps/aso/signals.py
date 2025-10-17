from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.forms import ValidationError
from .models import OrderTracking
import textwrap

@receiver(post_save, sender=OrderTracking)
def send_tracking_update_email(sender, instance, created, **kwargs):
    if created:
        order = instance.order
        user = order.user

        subject = f"Your Order {order.order_number} Status Update"
        message = textwrap.dedent(f"""
            Dear {user.first_name or "Valued Customer"},

            Your order **{order.order_number}** status has been updated to:  
            **{instance.status}**

            Details: {instance.description}  
            Date: {instance.date.strftime('%Y-%m-%d %H:%M')}

            Thank you for shopping with us!  

            Need help? Contact us:  
            📞 +234 1 700 0000  
            ✉️ support@aso-okemarketplace.ng  

            Preserving Nigeria’s textile heritage,  
            **The Aso Oke & Aso Ofi Marketplace Team**
        """)
        recipient_list = [user.email]

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


@receiver(pre_save, sender=OrderTracking)
def enforce_order_tracking_rules(sender, instance, **kwargs):
    # Define allowed status order
    STATUS_SEQUENCE = [
        'placed',
        'processing',
        'shipped',
        'in_transit',
        'delivered'
    ]

    # Get all existing tracking entries for the same order
    existing_entries = OrderTracking.objects.filter(order=instance.order).order_by('id')

    # Rule 1: Stop if delivered or cancelled already exists
    if existing_entries.filter(status='delivered').exists() or existing_entries.filter(status='cancelled').exists():
        # But allow cancelled to be added anytime
        if instance.status != 'cancelled':
            raise ValidationError(f"Cannot add more tracking after 'delivered' or 'cancelled' for order {instance.order.order_number}.")

    # Rule 2: Enforce sequence (cancelled can be anywhere)
    if instance.status != 'cancelled':
        if existing_entries.exists():
            last_status = existing_entries.last().status
            try:
                last_index = STATUS_SEQUENCE.index(last_status)
                new_index = STATUS_SEQUENCE.index(instance.status)
            except ValueError:
                raise ValidationError(f"Invalid status: {instance.status}")

            # Must be the immediate next status in the sequence
            if new_index != last_index + 1:
                raise ValidationError(f"Status '{instance.status}' must follow '{last_status}' in sequence.")
        else:
            # First status must be 'placed'
            if instance.status != 'placed':
                raise ValidationError("First tracking status must be 'placed'.")