

from decimal import Decimal

from celery import shared_task
from apps.aso.models import Product
from utils.Tasks.Emails.EmailForLimitedProducts import send_limited_day_announcement
from utils.decorators import checkBackgroundFeatureFlag
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled


@checkBackgroundFeatureFlag()
@shared_task
def set_limited_product():
    """
    Apply a discount to limited products using the PRODUCT_LIMITATION feature flag.
    The discount percentage is taken from the feature flag itself.
    """

    flag, enable = is_feature_enabled(FeatureNames.PRODUCT_LIMITATION.value)
    if not enable:
        return "⚠️ Limited product feature is disabled."
    
    if not flag.discount_percent or flag.discount_percent <= 0:
        return "⚠️ No discount percent defined for product limitation feature."
    
    if flag.is_active:
        return "⚠️ Limited product discount is already active."
    
    discount_percent = flag.discount_percent
    discount_decimal = Decimal(discount_percent) / Decimal('100')
    
    products = (
        Product.objects
        .filter(is_deleted=False, display_product=True)
        .order_by('-original_price')[:9]
    )
    
    if not products.exists():
        return "❌ No eligible products found."
    
    updated = 0
    for product in products:

        # Only update if needed
        base_discount = product.discount_percent or 0
        new_discount = min(base_discount + flag.discount_percent, 90)  # Cap at 90%
        product.discount_percent = new_discount
        product.current_price = product.original_price - (product.original_price * discount_decimal)
        product.is_limited = True
        product.badge = "Limited"
        product.save(update_fields=["discount_percent", "current_price", "is_limited", "badge"])
        updated += 1
        
    flag.is_active = True
    flag.save(update_fields=['is_active'])
    
    send_limited_day_announcement()

    return f"✅ Applied {discount_percent}% discount to {updated} limited products."