from decimal import Decimal
from apps.aso.models import Product
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled


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

    return f"✅ Unset limited product discount for {products.count()} products."