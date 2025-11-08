

from decimal import Decimal
from apps.aso.models import Product
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled


def set_limited_product():

    flag, enable = is_feature_enabled(FeatureNames.PRODUCT_LIMITATION.value)
    if not enable:
        return "⚠️ Limited product feature is disabled."
    
    products = (
        Product.objects
        .filter(is_deleted=False, display_product=True)
        .order_by('-original_price')[:9]
    )
    
    if not products.exists():
        return "❌ No eligible products found."
    
    for product in products:
        discount = Decimal('0.30')  # 30%
        product.discount_percent = 30
        product.current_price = product.original_price * (Decimal('1.00') - discount)
        product.save(update_fields=["discount_percent", "current_price"])

    return f"✅ Applied 30% discount to {products.count()} products."
    
    