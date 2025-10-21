
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