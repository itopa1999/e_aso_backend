from decimal import Decimal

from celery import shared_task
from apps.aso.models import Product
from utils.decorators import checkBackgroundFeatureFlag
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled
from utils.telegram_helpers import send_announcement
from django.conf import settings
from django.utils import timezone

@checkBackgroundFeatureFlag()
@shared_task
def unset_limited_product():
    """
    Remove or reset discounts applied by the PRODUCT_LIMITATION feature flag.
    """

    flag, enable = is_feature_enabled(FeatureNames.PRODUCT_LIMITATION.value)
    if enable:
        return "Limited product feature is still enabled."
    
    if not flag.discount_percent or flag.discount_percent <= 0:
        return "⚠️ No discount percent defined for product limitation feature."
    
    if not flag.is_active:
        return "⚠️ Limited product discount is not currently active."

    products = Product.objects.filter(is_deleted=False, display_product=True, is_limited=True)

    for product in products:
        base_discount = product.discount_percent or 0
        new_discount = max(base_discount - flag.discount_percent, 0)
        product.discount_percent = new_discount

        discount_decimal = Decimal(new_discount) / Decimal('100')
        product.current_price = product.original_price - (product.original_price * discount_decimal)
        product.is_limited = False
        product.badge = ""

        product.save(update_fields=['discount_percent', 'current_price', 'is_limited', 'badge'])

    flag.is_active = False
    flag.save(update_fields=['is_active'])
    
    message = f"""
    ⚠️ <b>LIMITED PRODUCT COLLECTION OFFER HAS ENDED!</b> ⚠️

    Hello shoppers! The <b>exclusive limited products promotion</b> has officially ended.

    We hope you had a chance to grab your favorites. Stay tuned for upcoming deals and special promotions!  

    🛍️ Visit our store to explore other products:  
    👉 <b><a href="{settings.BASE_URL}/index.html">Shop Now</a></b>

    Thank you for shopping with us! 💖
    """
    send_announcement(message)

    return f"✅ Unset limited product discount for {products.count()} products."