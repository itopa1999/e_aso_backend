from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from utils.Tasks.ApplyBlackFridayDiscount import apply_friday_discount
from utils.Tasks.Emails.EmailForFeedback import send_feedback_email_announcement
from utils.Tasks.Emails.EmailForFreeShipping import send_free_shipping_announcement
from utils.Tasks.Emails.EmailForProductAds import send_new_product_announcement
from utils.Tasks.Emails.EmailForRefferralDiscount import send_referral_program_announcement
from utils.Tasks.ResetBlackFridayDiscount import reset_friday_discount
from utils.Tasks.SetLimitedProduct import set_limited_product
from utils.Tasks.UnsetLimitedProduct import unset_limited_product
from utils.cache_manager import GlobalCache
from utils.email_sender import send_custom_email
from utils.enum import CacheKeys, FeatureNames
from .models import Cart, CartItem, FeatureFlag, LookUp, Order, OrderFeedBack, OrderItem, OrderReturn, OrderTracking, PaymentDetail, Product, ShippingAddress, WatchList
from utils.telegram_helpers import send_notification
import textwrap



@receiver(post_save, sender=OrderTracking)
def send_tracking_update_email(sender, instance, created, **kwargs):
    if created:
        order = instance.order
        user = order.user
        
        # --- Special message for first status: "Placed" ---
        if instance.status.lower() == "placed":
            email_message = textwrap.dedent(f"""
                We’ve just received your order {order.order_number}! 🎉

                Our team is getting everything ready for you.
                We’ll keep you updated as your order moves through each stage.

                Thank you for trusting us!
            """).strip()

            telegram_message = textwrap.dedent(f"""
                🎉 Order Received!

                We’ve received your order {order.order_number}.
                Our team is preparing it now, you’ll get updates as it progresses.
            """).strip()

        else:
            # --- Default message for all other status updates ---
            email_message = textwrap.dedent(f"""
                Your order {order.order_number} has been updated.

                Status: {instance.status}
                Details: {instance.description}
                Date: {instance.date.strftime('%Y-%m-%d %H:%M')}

                Thank you for shopping with us!
            """).strip()

            telegram_message = textwrap.dedent(f"""
                📦 Order Update

                Order: {order.order_number}
                Status: {instance.status}
                Details: {instance.description}
                Date: {instance.date.strftime('%Y-%m-%d %H:%M')}
            """).strip()

        # --- Send Email ---
        send_custom_email(
            subject=f"Order {order.order_number} Update",
            recipient_email=user.email,
            message=email_message,
            greeting_name=user.first_name or "Valued Customer"
        )

        # --- Send Telegram Notification ---
        if user.telegram_notifications_enabled and user.telegram_user_chat_id:
            send_notification(
                message=telegram_message,
                chat_id=user.telegram_user_chat_id
            )
                
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
    existing_entries = OrderTracking.objects.filter(order=instance.order, is_deleted = False).order_by('id')

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
            
            
            
def clear_order_cache(user_id, order_id=None):
    """Clear both user order list and order detail cache."""
    if not user_id:
        return

    # Clear user’s order list cache
    GlobalCache.delete(CacheKeys.format(CacheKeys.USER_ORDERS, user_id=user_id))
    GlobalCache.delete(CacheKeys.format(CacheKeys.USER_PROFILE, user_id=user_id))

    # Clear specific order detail cache (if provided)
    if order_id:
        GlobalCache.delete(CacheKeys.format(CacheKeys.ORDER_DETAIL, user_id=user_id, order_id=order_id))
        GlobalCache.delete(CacheKeys.format(CacheKeys.USER_ORDER_TRACKING, user_id=user_id, order_id=order_id))



@receiver([post_save, post_delete], sender=Order)
@receiver([post_save, post_delete], sender=OrderItem)
@receiver([post_save, post_delete], sender=ShippingAddress)
@receiver([post_save, post_delete], sender=OrderTracking)
@receiver([post_save, post_delete], sender=PaymentDetail)
@receiver([post_save, post_delete], sender=OrderFeedBack)
@receiver([post_save, post_delete], sender=OrderReturn)
def order_related_model_changed(sender, instance, **kwargs):
    """Automatically clear cache when any related order model changes."""
    user_id = None
    order_id = None

    # Figure out user and order depending on the model
    if hasattr(instance, "order"):  # For related models
        order = getattr(instance, "order", None)
        if order:
            order_id = order.id
            user_id = getattr(order.user, "id", None)
    elif isinstance(instance, Order):
        order_id = instance.id
        user_id = getattr(instance.user, "id", None)

    # Perform cache clearing
    clear_order_cache(user_id, order_id)


@receiver([post_save, post_delete], sender=WatchList)
def watchlist_model_changed(sender, instance, **kwargs):
    cache_key = CacheKeys.format(CacheKeys.USER_WATCHLIST, user_id=instance.user.id)
    GlobalCache.delete(cache_key)
    
    
@receiver([post_save, post_delete], sender=Product)
def product_model_changed(sender, instance, **kwargs):
    cache_key = CacheKeys.PRODUCT_LIST
    GlobalCache.delete(cache_key)
    highest_price_key = CacheKeys.HIGHEST_PRICE_PRODUCTS.value
    GlobalCache.delete(highest_price_key)
    
    
@receiver([post_save, post_delete], sender=Product)
def clear_product_detail_cache(sender, instance, **kwargs):
    cache_key = CacheKeys.format(CacheKeys.PRODUCT_DETAIL, product_id=instance.id)
    GlobalCache.delete(cache_key)
    
    
@receiver([post_save, post_delete], sender=FeatureFlag)
def clear_feature_detail_cache(sender, instance, **kwargs):
    cache_key = CacheKeys.format(CacheKeys.FEATURE_FLAGS, feature_name=instance.name)
    GlobalCache.delete(cache_key)
    
    
@receiver([post_save, post_delete], sender=LookUp)
def lookup_model_changed(sender, instance, **kwargs):
    cache_key = CacheKeys.LOOKUP
    GlobalCache.delete(cache_key)
    
    
@receiver([post_save, post_delete], sender=Cart)
@receiver([post_save, post_delete], sender=CartItem)
def watchlist_model_changed(sender, instance, **kwargs):
    
    if isinstance(instance, Cart):
        user_id = instance.user.id
    elif isinstance(instance, CartItem):
        user_id = instance.cart.user.id
    else:
        return
    cache_key1 = CacheKeys.format(CacheKeys.USER_WATCHLIST, user_id=user_id)
    cache_key = CacheKeys.format(CacheKeys.USER_CART, user_id=user_id)
    GlobalCache.delete(cache_key)
    GlobalCache.delete(cache_key1)
    
    
    
@receiver([post_save, post_delete], sender=Cart)
@receiver([post_save, post_delete], sender=CartItem)
@receiver([post_save, post_delete], sender=WatchList)
def clear_cart_watchlist_cache(sender, instance, **kwargs):

    user_id = getattr(instance, "user_id", None) or getattr(instance.cart, "user_id", None)
    if user_id:
        cache_key = CacheKeys.format(CacheKeys.USER_WATCHLISTCART, user_id=user_id)
        GlobalCache.delete(cache_key)
        
        

@receiver(post_save, sender=FeatureFlag)
def handle_featureflag_update(sender, instance, created, **kwargs):
    """
    Automatically trigger feature logic when FeatureFlag is updated.
    """

    # Skip logic for creation — only handle updates
    if created:
        return

    # Check which feature name it is
    feature_name = instance.name
    is_enabled = instance.is_enabled
    
    print(f"[FeatureFlag] Detected update for {feature_name}, enabled={is_enabled}")

    try:
        # 🏷️ Match the feature name to your handlers
        if feature_name == FeatureNames.BLACK_FRIDAY.value:
            if is_enabled:
                result = apply_friday_discount()
            else:
                result = reset_friday_discount()

        elif feature_name == FeatureNames.PRODUCT_LIMITATION.value:
            if is_enabled:
                result = set_limited_product()
            else:
                result = unset_limited_product()
                
        elif feature_name == FeatureNames.FREE_DELIVERY.value:
            if is_enabled:
                result = send_free_shipping_announcement()
            else:
                if instance.is_active:
                    instance.is_active = False
                    instance.save(update_fields=['is_active'])
                    
        elif feature_name == FeatureNames.REFERRAL_SYSTEM.value:
            if is_enabled:
                result = send_referral_program_announcement()
            else:
                 if instance.is_active:
                    instance.is_active = False
                    instance.save(update_fields=['is_active'])
                    
        elif feature_name == FeatureNames.NEW_PRODUCT_ANNOUNCEMENT.value:
            if is_enabled:
                # Fetch latest product instance
                latest_product = Product.objects.filter(is_deleted=False, display_product=True).order_by("-created_at").exists()
                if latest_product:
                    result = send_new_product_announcement()
                else:
                    result = "⚠️ No new product found to announce."
            else:
                if instance.is_active:
                    instance.is_active = False
                    instance.save(update_fields=['is_active'])
        elif feature_name == FeatureNames.FEEDBACK.value:
            if is_enabled:
                # Logic for enabling feedback feature can be added here
                result = send_feedback_email_announcement()
            else:
                if instance.is_active:
                    instance.is_active = False
                    instance.save(update_fields=['is_active'])
        else:
            result = f"⚠️ No handler registered for {feature_name}."

        print(f"[FeatureFlag] {feature_name} updated — {result}")

    except Exception as e:
        print(f"❌ Error while running feature handler for {feature_name}: {e}")
        
