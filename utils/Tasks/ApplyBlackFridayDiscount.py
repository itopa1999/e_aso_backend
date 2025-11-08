
from decimal import Decimal
from apps.aso.models import Product
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled


def apply_friday_discount():

    flag, enable = is_feature_enabled(FeatureNames.BLACK_FRIDAY.value)
    if not enable:
        return "Friday discount feature is disabled."
    
    products = Product.objects.filter(is_deleted=False, display_product=True)

    for product in products:
        base_discount = product.discount_percent or 0
        new_discount = min(base_discount + 20, 90)  # Cap at 90%
        product.discount_percent = new_discount
        discount_decimal = Decimal(new_discount) / Decimal('100')
        product.current_price = product.original_price - (product.original_price * discount_decimal)
        product.save(update_fields=['discount_percent', 'current_price'])
        
    return f"✅ Applied Friday discount to {products.count()} products."
    