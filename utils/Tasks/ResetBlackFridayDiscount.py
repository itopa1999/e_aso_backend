from decimal import Decimal

from celery import shared_task
from django.conf import settings
from apps.aso.models import Product
from utils.decorators import checkBackgroundFeatureFlag
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled
from utils.telegram_helpers import send_announcement



@checkBackgroundFeatureFlag()
@shared_task
def reset_friday_discount():

    flag, enable = is_feature_enabled(FeatureNames.BLACK_FRIDAY.value)
    if enable:
        return "Friday discount feature is disabled."
    
    if not flag.discount_percent or flag.discount_percent <= 0:
        return "⚠️ No discount percent defined for Black Friday feature."
    
    if not flag.is_active:
        return "⚠️ Black Friday discount is not currently active."
    
    products = Product.objects.filter(is_deleted=False, display_product=True)
    for product in products:
        base_discount = product.discount_percent or 0
        new_discount = max(base_discount - flag.discount_percent, 0)  # Ensure discount doesn't go below 0%
        product.discount_percent = new_discount
        discount_decimal = Decimal(new_discount) / Decimal('100')
        product.current_price = product.original_price - (product.original_price * discount_decimal)
        product.save(update_fields=['discount_percent', 'current_price'])
        
    flag.is_active = False
    flag.save(update_fields=['is_active'])
    
    message = f"""
    ⏰ <b>Black Friday Discount Day has ended!</b> ⏰

    The special <b>discounts on all products</b> have now expired.  
    Hope you grabbed your favorites in time!  

    🛒 Visit our store to see current offers: <b><a href="{settings.BASE_URL}/index.html">Shop now</a></b>
    """
    send_announcement(message)
    
    return f"✅ Reset Friday discount for {products.count()} products."

