
from decimal import Decimal
from apps.aso.models import Product
from utils.Tasks.Emails.EmailForBlackFriday import send_discount_day_announcement
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled


def apply_friday_discount():

    flag, enable = is_feature_enabled(FeatureNames.BLACK_FRIDAY.value)
    if not enable:
        return "Friday discount feature is disabled."
    
    if not flag.discount_percent or flag.discount_percent <= 0:
        return "⚠️ No discount percent defined for product black friday feature."
    
    if flag.is_active:
        return "⚠️ Black Friday discount is already active."
    
    products = Product.objects.filter(is_deleted=False, display_product=True)
    updated_count = 0
    
    for product in products:
        base_discount = product.discount_percent or 0
        new_discount = min(base_discount + flag.discount_percent, 90)  # Cap at 90%
        product.discount_percent = new_discount
        discount_decimal = Decimal(new_discount) / Decimal('100')
        product.current_price = product.original_price - (product.original_price * discount_decimal)
        product.save(update_fields=['discount_percent', 'current_price'])
        updated_count += 1
        
    flag.is_active = True
    flag.save(update_fields=['is_active'])
    
    send_discount_day_announcement()
        
    return f"✅ Applied Friday discount to {updated_count} products."
