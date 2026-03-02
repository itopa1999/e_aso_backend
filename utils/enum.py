
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
    PRODUCT_LIMITATION = "Product Limitation"
    NEW_PRODUCT_ANNOUNCEMENT = "New Product Announcement"
    BACKGROUND_TASKS = "Background Tasks"
    FEEDBACK = "Feedback"
    

    @classmethod
    def values(cls):
        """Return all enum values as a list"""
        return [flag.value for flag in cls]

    @classmethod
    def choices(cls):
        """Return choices tuple for Django model fields"""
        return [(flag.value, flag.value) for flag in cls]
    
    

class GroupNames(Enum):
    ADMIN = "Admin"
    CUSTOMER = "Customer"
    RIDER = "Rider"
    
    @classmethod
    def values(cls):
        """Return all enum values as a list"""
        return [group.value for group in cls]
    
    
    
    
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
    HIGHEST_PRICE_PRODUCTS = "highest_price_products"
    # FEATURED_PRODUCTS = "featured_products"
    # PRODUCT_CATEGORY_LIST = "product_category_list"

    # Order-related keys
    ORDER_DETAIL = "order_detail_{user_id}_{order_id}"
    USER_ORDERS = "user_orders_{user_id}"
    USER_ORDER_TRACKING = "user_order_tracking_{user_id}_{order_id}"

    # Notification-related keys
    USER_NOTIFICATIONS = "user_notifications_{user_id}"
    USER_NOTIFICATIONS_RECENT = "user_notifications_recent_{user_id}"

    # Misc / site-wide
    LOOKUP = "lookup"
    CUSTOMER_FEEDBACK_LIST = "customer_feedback_list"
    CONTACT_FORM_SUBMISSION = "contact_form_submission"
    CUSTOMER_TRANSACTIONS = "customer_transactions"
    FEATURE_FLAGS = "feature_flag_{feature_name}"
    BANNER = "banner_{category}"
    
    # telgram bot
    telegram_user_tokens = "telegram_user_tokens_{user_id}"
    telegram_user_login_codes = "telegram_user_login_codes_{user_id}"
    telegram_user_login_stage = "telegram_user_login_stage_{user_id}"
    
    telegram_user_shipping_info = "telegram_user_shipping_info_{user_id}"
    telegram_user_shipping_stage = "telegram_user_shipping_stage_{user_id}"
    
    telegram_user_contact_info = "telegram_user_contact_info_{user_id}"
    telegram_user_contact_stage = "telegram_user_contact_stage_{user_id}"
    
    telegram_user_search_stage = "telegram_user_search_stage_{user_id}"

    @classmethod
    def format(cls, key, **kwargs):
        """
        Helper method to fill in placeholders for formatted keys.
        Example:
            CacheKeys.format(CacheKeys.USER_PROFILE, user_id=5)
        """
        return key.value.format(**kwargs)
    
    

class TransactionType(Enum):
    PURCHASE = "Purchase"
    REFUND = "Refund"

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]
    
    
class ContactFormStatus(Enum):
    NEW = "New"
    REPLIED = "Replied"

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]


class TransactionChannel(Enum):
    FLUTTERWAVE = "Flutterwave"
    PAYSTACK = "Paystack"
    BANK_TRANSFER = "Bank Transfer"
    WALLET = "Wallet"

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]


class TransactionStatus(Enum):
    PENDING = "Pending"
    SUCCESS = "Success"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]


class PaymentStatus(Enum):
    PENDING = "Pending Payment"
    FAILED = "Payment Failed"
    CONFIRMED = "Payment Confirmed"
    CANCELLED = "Cancelled"

    @classmethod
    def choices(cls):
        return [(key.name.lower(), key.value) for key in cls]


class PaymentGateway(Enum):
    PAYSTACK = "paystack"
    FLUTTERWAVE = "flutterwave"
    MONNIFY = "monnify"

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]


class OrderTrackingStatus(Enum):
    PLACED = "placed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]
    
    @classmethod
    def get_descriptions(cls):
        return {
            'placed': "Your order has been updated to Placed. 🎉 We've received your order! Our team is now processing it and will get it ready for shipment soon.",
            'processing': "Your order has been updated to Processing. 📦 Your order is being carefully prepared and packaged. We're almost ready to ship!",
            'shipped': "Your order has been updated to Shipped. 🚚 Your package is on its way to you! You can track it using the tracking number provided.",
            'in_transit': "Your order has been updated to In Transit. 🚛 Your order is on its way! It should arrive soon. Thank you for your patience!",
            'delivered': "Your order has been updated to Delivered. ✅ Your order has been delivered! We hope you enjoy your purchase. Thank you for shopping with us!",
            'cancelled': "Your order has been updated to Cancelled. ❌ Your order has been cancelled. If you have any questions, please contact our support team.",
        }


class NotificationType(Enum):
    SYSTEM = "system"
    UPDATES = "updates"
    PROMOTION = "promos"

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]