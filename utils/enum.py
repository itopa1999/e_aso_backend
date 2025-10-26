
from enum import Enum
class LookUpsCategories:
    PRODUCT_CATEGORY = 'product_cat'
    BADGE_CATEGORY = 'badge_cat'
    



class FeatureNames(Enum):
    PROMO_BANNER = "Promo Banner"
    REFERRAL_SYSTEM = "Referral System"
    FREE_DELIVERY = "Free Delivery"
    CART_DISCOUNT = "Cart Discount"
    BLACK_FRIDAY = "Black Friday"

    @classmethod
    def values(cls):
        """Return all enum values as a list"""
        return [flag.value for flag in cls]

    @classmethod
    def choices(cls):
        """Return choices tuple for Django model fields"""
        return [(flag.value, flag.value) for flag in cls]
    
    
    
class BannerCategoryNames(Enum):
    PROMO = "Promo"
    INDEX = "index"
    ADS = "ads"
    SUPPORT = "support"
    BLACK_FRIDAY = "black friday"
    HERO = "hero"

    @classmethod
    def choices(cls):
        """Return choices tuple for Django model fields"""
        return [(banner.value, banner.value) for banner in cls]
    
    
    
class CacheKeys(Enum):
    """
    Centralized cache key names for consistency across the project.
    Always use CacheKeys.KEY_NAME.value when accessing cache.
    """

    # User-related keys
    USER_PROFILE = "user_profile_{user_id}"
    USER_CART = "user_cart_{user_id}"
    USER_WATCHLIST = "user_watchlist_{user_id}"
    USER_WATCHLISTCART = "user_watchlist_cart_{user_id}"

    # Product-related keys
    PRODUCT_LIST = "product_list_all"
    PRODUCT_DETAIL = "product_detail_{product_id}"
    # FEATURED_PRODUCTS = "featured_products"
    # PRODUCT_CATEGORY_LIST = "product_category_list"

    # Order-related keys
    ORDER_DETAIL = "order_detail_{user_id}_{order_id}"
    USER_ORDERS = "user_orders_{user_id}"

    # Misc / site-wide
    LOOKUP = "lookup"
    FEATURE_FLAGS = "feature_flag_{feature_name}"
    BANNER = "banner_{category}"

    @classmethod
    def format(cls, key, **kwargs):
        """
        Helper method to fill in placeholders for formatted keys.
        Example:
            CacheKeys.format(CacheKeys.USER_PROFILE, user_id=5)
        """
        return key.value.format(**kwargs)