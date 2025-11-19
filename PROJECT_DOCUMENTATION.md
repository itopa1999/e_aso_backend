# E-Sell Backend - Complete Project Documentation

**Project:** E-Sell Backend  
**Repository:** e_aso_backend  
**Owner:** itopa1999  
**Branch:** main  
**Last Updated:** November 12, 2025

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Architecture](#architecture)
5. [Database Models](#database-models)
6. [Feature Flags System](#feature-flags-system)
7. [Celery & Background Tasks](#celery--background-tasks)
8. [Redis & Caching](#redis--caching)
9. [API Routes & Endpoints](#api-routes--endpoints)
10. [Authentication & Authorization](#authentication--authorization)
11. [Middleware](#middleware)
12. [Settings Configuration](#settings-configuration)
13. [Docker Setup](#docker-setup)
14. [Testing](#testing)
15. [Logging](#logging)
16. [Best Practices](#best-practices)

---

## 1. Project Overview

E-Sell Backend is a Django-based e-commerce platform that provides a comprehensive API for managing products, orders, users, and administrative functions. The system is designed with scalability in mind, utilizing Celery for background tasks, Redis for caching, and PostgreSQL for data persistence.

### Key Features
- Product catalog management with categories, colors, sizes
- Shopping cart and wishlist functionality
- Order management and tracking
- User authentication with magic links
- Referral system
- Feature flag system for controlled rollouts
- Background task processing
- Admin analytics dashboard
- Payment integration with Paystack
- Delivery fee calculation
- Black Friday and promotional campaigns

---

## 2. Technology Stack

### Core Framework
- **Django 5.2.7** - Web framework
- **Django REST Framework 3.15.2** - API framework
- **PostgreSQL 15** - Primary database
- **Python 3.x** - Programming language

### Background Processing
- **Celery 5.5.3** - Distributed task queue
- **Redis** - Message broker and cache backend

### API Documentation
- **drf-yasg 1.21.7** - Swagger/OpenAPI documentation
- **drf-standardized-errors 0.14.1** - Consistent error responses

### Authentication
- **djangorestframework-simplejwt 5.3.1** - JWT authentication

### Additional Tools
- **django-redis 6.0.0** - Redis cache backend
- **django-cors-headers 4.4.0** - CORS support
- **django-filter 25.1** - Query filtering
- **django-health-check 3.20.0** - Health monitoring
- **Pillow 10.4.0** - Image processing
- **pytest 8.4.2** - Testing framework

---

## 3. Project Structure

```
E_Sell_backend/
│
├── apps/                          # Application modules
│   ├── administrator/             # Admin-specific functionality
│   │   ├── BLL/                   # Business Logic Layer
│   │   │   ├── Commands/          # Write operations
│   │   │   └── Queries/           # Read operations
│   │   ├── migrations/            # Database migrations
│   │   ├── tests/                 # Unit tests
│   │   ├── admin.py               # Django admin config
│   │   ├── analytics_views.py     # Analytics endpoints
│   │   ├── apps.py                # App configuration
│   │   ├── models.py              # Data models
│   │   ├── serializers.py         # DRF serializers
│   │   ├── signals.py             # Django signals
│   │   ├── urls.py                # URL routing
│   │   ├── utils.py               # Helper functions
│   │   └── views.py               # API views
│   │
│   ├── aso/                       # Main e-commerce app
│   │   ├── BBL/                   # Business Logic Layer
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── deliveryFee.py         # Delivery fee logic
│   │   ├── models.py              # Product, Order, Cart models
│   │   ├── paystack.py            # Payment integration
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── rider/                     # Delivery rider management
│   │   ├── BLL/
│   │   ├── migrations/
│   │   ├── tests/
│   │   └── [standard Django app files]
│   │
│   └── users/                     # User management
│       ├── BBL/
│       ├── migrations/
│       ├── tests/
│       ├── manager.py             # Custom user manager
│       └── [standard Django app files]
│
├── backend/                       # Project settings
│   ├── settings/                  # Environment-specific settings
│   │   ├── __init__.py
│   │   ├── base.py                # Base settings
│   │   ├── dev.py                 # Development settings
│   │   ├── prod.py                # Production settings
│   │   └── staging.py             # Staging settings
│   ├── asgi.py                    # ASGI config
│   ├── celery.py                  # Celery configuration
│   ├── exception_formatter.py     # Error formatting
│   ├── exceptions.py              # Custom exceptions
│   ├── schema.py                  # Swagger schema config
│   ├── test_settings.py           # Test configuration
│   ├── urls.py                    # Root URL config
│   └── wsgi.py                    # WSGI config
│
├── utils/                         # Shared utilities
│   ├── Middlewares/               # Custom middleware
│   │   ├── log_exceptions.py      # Exception logging
│   │   └── threadlocals.py        # Thread-local storage
│   ├── Tasks/                     # Celery tasks
│   │   ├── Emails/                # Email tasks
│   │   ├── tests/
│   │   ├── ApplyBlackFridayDiscount.py
│   │   ├── ResetBlackFridayDiscount.py
│   │   ├── SetLimitedProduct.py
│   │   ├── UnsetLimitedProduct.py
│   │   ├── BadgeUpdate.py
│   │   └── tasks.py               # Task definitions
│   ├── base_admin.py              # Base admin class
│   ├── base_model.py              # Base model class
│   ├── base_result.py             # Result object pattern
│   ├── cache_manager.py           # Cache utilities
│   ├── decorators.py              # Custom decorators
│   ├── email_sender.py            # Email utilities
│   ├── enum.py                    # Enumerations
│   ├── feature_flags.py           # Feature flag logic
│   ├── log_helpers.py             # Logging helpers
│   ├── logger.py                  # Logger configuration
│   ├── lookups.json               # Lookup data
│   ├── magic_link.py              # Magic link auth
│   ├── permissions.py             # Custom permissions
│   └── swagger.py                 # Swagger utilities
│
├── logs/                          # Application logs
├── media/                         # User-uploaded files
│   ├── banners/
│   └── products/
├── staticfiles/                   # Static files (CSS, JS)
├── templates/                     # HTML templates
│
├── db.sqlite3                     # SQLite database (dev)
├── docker-compose.yml             # Docker orchestration
├── Dockerfile                     # Docker image definition
├── entrypoint.sh                  # Docker entrypoint script
├── main.py                        # Main application entry
├── manage.py                      # Django management script
├── Procfile                       # Heroku deployment
├── pytest.ini                     # Pytest configuration
├── requirements.txt               # Python dependencies
└── ReadMe                         # Project readme
```

---

## 4. Architecture

### Application Layer Architecture

The project follows a layered architecture pattern:

```
┌─────────────────────────────────────────┐
│         API Layer (Views)               │
│  - REST endpoints                       │
│  - Request validation                   │
│  - Response formatting                  │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│      Business Logic Layer (BLL)         │
│  - Commands (Write operations)          │
│  - Queries (Read operations)            │
│  - Business rules                       │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│       Data Access Layer (Models)        │
│  - ORM models                           │
│  - Database operations                  │
│  - Data validation                      │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         Database (PostgreSQL)           │
└─────────────────────────────────────────┘
```

### Background Processing Architecture

```
┌─────────────┐         ┌─────────────┐
│   Django    │────────▶│    Redis    │
│   Views     │ Enqueue │   Broker    │
└─────────────┘         └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │   Celery    │
                        │   Workers   │
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │  Task Queue │
                        │  Processing │
                        └─────────────┘
```

### Caching Strategy

```
Request ──▶ Check Cache (Redis)
                │
         ┌──────┴──────┐
         │             │
      Hit│             │Miss
         ▼             ▼
    Return Data   Query Database
                       │
                   Save to Cache
                       │
                   Return Data
```

---

## 5. Database Models

### Core Models Overview

#### **apps/aso/models.py** - Main E-commerce Models

##### **LookUp**
Generic lookup table for categories and classifications.
```python
Fields:
- name: CharField (unique, indexed)
- category: CharField
- description: TextField
- is_deleted: Boolean (soft delete)
- created_at, updated_at: Timestamps
```

##### **Product**
Core product model with pricing, discounts, and display options.
```python
Fields:
- product_number: Auto-generated (#AO-P-XXXX)
- category: ManyToMany → LookUp
- title: CharField (indexed)
- description: TextField
- original_price: DecimalField
- current_price: DecimalField (calculated from discount)
- discount_percent: PositiveIntegerField (0-100)
- rating: FloatField
- reviews_count: PositiveIntegerField
- badge: CharField (e.g., "New", "Sale")
- main_image: ImageField
- display_product: Boolean
- is_limited: Boolean

Key Methods:
- save(): Auto-generates product_number, calculates discounts
- get_active_products(): Optimized query with prefetch_related
- category_names: Property returning comma-separated categories

Indexes:
- title, current_price, product_number
- Partial index on non-deleted products
```

##### **ProductColor**
Product color variants.
```python
Fields:
- product: ForeignKey → Product
- color_name: CharField
- hex_code: CharField

Constraints:
- unique_together: (product, color_name)
```

##### **ProductSize**
Product size variants.
```python
Fields:
- product: ForeignKey → Product
- size_label: CharField

Constraints:
- unique_together: (product, size_label)
```

##### **ProductDetail**
Detailed product information organized by tabs.
```python
Fields:
- product: ForeignKey → Product
- tab: CharField (choices: description, details, shipping)
- title: CharField
- content: TextField
```

##### **ProductImage**
Product gallery images.
```python
Fields:
- product: ForeignKey → Product
- image: ImageField
- alt_text: CharField
```

##### **WatchList**
User's wishlist/watchlist items.
```python
Fields:
- product: ForeignKey → Product
- user: ForeignKey → User

Constraints:
- unique_together: (user, product)
```

##### **Cart**
Shopping cart with dynamic pricing calculations.
```python
Fields:
- user: OneToOne → User
- state: CharField (for delivery fee calculation)
- _cached_flags: Internal cache for feature flags

Key Methods:
- subtotal(): Sum of all cart items
- shipping_cost(): Based on state and FREE_DELIVERY flag
- discount(): Referral discount (20% if qualified)
- total(): subtotal - discount + shipping_cost
- _get_feature_flags(): Caches feature flags during instance lifecycle

Optimization:
- Caches feature flags to avoid repeated DB queries
```

##### **CartItem**
Individual items in shopping cart.
```python
Fields:
- cart: ForeignKey → Cart
- product: ForeignKey → Product
- quantity: PositiveIntegerField
- desc: JSONField (color, size selections)
- _cached_subtotal: Internal cache

Key Methods:
- subtotal(): product.current_price × quantity (cached)

Constraints:
- unique_together: (cart, product)
```

##### **Order**
Customer orders with tracking.
```python
Fields:
- user: ForeignKey → User
- order_number: Auto-generated (#AO-OD-XXXX)
- tracking_number: Auto-generated (#AO-OT-XXXX)
- other_info: TextField
- subtotal, shipping_fee, discount, total: DecimalFields
- carrier: CharField (default: "Aso Oke Express")
- dispatcher: ForeignKey → User (rider)
- delivery_date: DateField
- estimated_delivery_date: DateField (auto: +7 days)

Key Methods:
- save(): Auto-generates order/tracking numbers, sets estimated delivery
- get_order_with_details(): Optimized query with all relations

Optimization:
- Single query for both order_number and tracking_number generation
- Uses .only('id') to minimize data transfer
```

##### **OrderItem**
Items within an order (snapshot of product at purchase time).
```python
Fields:
- order: ForeignKey → Order
- product: ForeignKey → Product
- quantity: PositiveIntegerField
- price: DecimalField (snapshot at purchase)
- desc: JSONField

Key Methods:
- total_price(): price × quantity

Constraints:
- unique_together: (order, product)
```

##### **ShippingAddress**
Delivery address for orders.
```python
Fields:
- order: OneToOne → Order
- first_name, last_name: CharField
- address: CharField
- apartment: CharField (optional)
- city, state: CharField
- phone, alt_phone: CharField
```

##### **PaymentDetail**
Payment method information.
```python
Fields:
- order: OneToOne → Order
- method: CharField (e.g., "Mastercard", "Bank Transfer")
```

##### **OrderTracking**
Order status tracking events.
```python
Fields:
- order: ForeignKey → Order
- status: CharField (choices: placed, processing, shipped, in_transit, delivered, cancelled)
- date: DateTimeField
- description: TextField
- completed: Boolean

Constraints:
- unique_together: (status, order)
```

##### **OrderFeedBack**
Customer feedback on completed orders.
```python
Fields:
- order: ForeignKey → Order
- stars: PositiveSmallIntegerField
- comment: TextField
```

##### **OrderReturn**
Order return requests.
```python
Fields:
- order: ForeignKey → Order
- reason: CharField
- message: TextField
```

##### **FeatureFlag**
Dynamic feature toggle system.
```python
Fields:
- name: CharField (unique, from FeatureNames enum)
- users: ManyToMany → User (optional specific users)
- description: TextField
- is_enabled: Boolean
- start_date, end_date: DateTimeField
- discount_percent: PositiveIntegerField
- count: PositiveIntegerField
- is_active: Boolean

Key Methods:
- clean(): Validates name, dates, discount_percent
- save(): Runs full_clean() before saving

Validation Rules:
- Name must be in FeatureNames enum
- If enabled:
  - discount_percent > 0
  - start_date and end_date must be set
  - start_date cannot be in past
  - end_date must be after start_date
```

### Model Relationships Diagram

```
User ──────────────┬────────────────┬──────────────┐
                   │                │              │
                   ▼                ▼              ▼
              WatchList          Cart          Order
                   │              │              │
                   │              ├─────────────┬┴────────────┐
                   │              ▼             ▼             ▼
                   │          CartItem    OrderItem   ShippingAddress
                   │              │             │             
                   │              ▼             │        PaymentDetail
                   └────────▶ Product ◀─────────┘             │
                                  │                           │
                        ┌─────────┼─────────┐                 │
                        ▼         ▼         ▼                 ▼
                  ProductColor ProductSize ProductImage  OrderTracking
                              ProductDetail                    │
                                                               ▼
                                                         OrderFeedBack
                                                         OrderReturn
```

---

## 6. Feature Flags System

### Overview
The feature flag system allows controlled rollout of features without code deployment. Features can be enabled globally or for specific users with time-based activation.

### Feature Flag Types (utils/enum.py)

```python
class FeatureNames(Enum):
    PROMO_BANNER = "Promo Banner"
    REFERRAL_SYSTEM = "Referral System"
    FREE_DELIVERY = "Free Delivery"
    CART_DISCOUNT = "Cart Discount"
    BLACK_FRIDAY = "Black Friday"
    PRODUCT_LIMITATION = "Product Limitation"
    NEW_PRODUCT_ANNOUNCEMENT = "New Product Announcement"
    BACKGROUND_TASKS = "Background Tasks"
```

### Feature Flag Logic (utils/feature_flags.py)

#### `is_feature_enabled(flag_name, user=None)`

**Rules:**
- ✅ Flag enabled + no users assigned → Enabled for everyone
- ✅ Flag enabled + users assigned → Enabled only for those users
- ❌ Flag disabled or not found → Disabled
- ⚠️ Invalid flag name → Raises `ImproperlyConfigured`

**Returns:** `(flag_object, boolean)`

**Example Usage:**
```python
from utils.feature_flags import is_feature_enabled
from utils.enum import FeatureNames

# Check global flag
flag, enabled = is_feature_enabled(FeatureNames.FREE_DELIVERY.value)
if enabled:
    # Apply free delivery logic
    pass

# Check user-specific flag
flag, enabled = is_feature_enabled(FeatureNames.REFERRAL_SYSTEM.value, user=request.user)
if enabled:
    # Apply referral discount
    pass
```

### Database Model
```python
FeatureFlag Model:
- name: Must be from FeatureNames enum
- is_enabled: Global enable/disable switch
- users: Specific users (empty = everyone)
- start_date/end_date: Time-based activation
- discount_percent: Associated discount value
- is_active: Runtime state tracking
```

### Admin Interface
Feature flags are managed through Django admin:
- `/backdoor/` → FeatureFlag section
- Create/Edit flags with validation
- Assign specific users
- Set time windows and discount percentages

### Integration Examples

#### Cart Discount (apps/aso/models.py)
```python
class Cart(BaseModel):
    def discount(self):
        flag, enabled = self._get_feature_flags()['referral_system']
        if not enabled or getattr(self.user, "referral_used_purchase", False):
            return Decimal("0.00")
        
        if getattr(self.user, "is_referral_qualified", False):
            return self.subtotal() * Decimal("0.20")
        
        return Decimal("0.00")
```

#### Free Delivery (apps/aso/models.py)
```python
class Cart(BaseModel):
    def shipping_cost(self):
        flag, enabled = self._get_feature_flags()['free_delivery']
        if enabled:
            return Decimal("0.00")
        return Decimal(DELIVERY_FEES.get(self.state, 0))
```

#### API Endpoint (apps/aso/views.py)
```python
class CheckFeatureFlagView(APIView):
    """
    GET /aso/api/product/feature-flag/{feature_name}/
    Returns: {"enabled": true/false}
    """
    pass
```

---

## 7. Celery & Background Tasks

### Celery Configuration (backend/celery.py)

```python
# Celery app initialization
app = Celery('aso-backend')

# Settings
- Broker: Redis
- Result Backend: Redis
- Serializer: JSON
- Timezone: Africa/Lagos
- Auto-discover tasks in installed apps

# Task Imports
- utils.Tasks.tasks
- utils.Tasks.ApplyBlackFridayDiscount
- utils.Tasks.ResetBlackFridayDiscount
- utils.Tasks.SetLimitedProduct
- utils.Tasks.UnsetLimitedProduct
- utils.Tasks.Emails.* (all email tasks)
```

### Background Task Decorator (utils/decorators.py)

```python
@checkBackgroundFeatureFlag(feature_name=FeatureNames.BACKGROUND_TASKS.value)
```

**How it works:**
1. Checks if BACKGROUND_TASKS feature flag is enabled
2. If enabled → Runs task asynchronously via Celery
3. If disabled → Runs task synchronously (blocking)

**Example Usage:**
```python
@checkBackgroundFeatureFlag()
@shared_task
def my_task(arg1, arg2):
    # Task logic
    pass

# Calling the task
my_task(1, 2)  # Auto-decides sync vs async based on feature flag
```

### Task Categories

#### 1. Discount Tasks
**ApplyBlackFridayDiscount.py**
```python
@checkBackgroundFeatureFlag()
@shared_task
def apply_friday_discount():
    """
    - Checks BLACK_FRIDAY feature flag
    - Applies additional discount to all products
    - Recalculates current_price
    - Sets flag.is_active = True
    - Sends announcement emails
    """
```

**ResetBlackFridayDiscount.py**
```python
@checkBackgroundFeatureFlag()
@shared_task
def reset_friday_discount():
    """
    - Reverts Black Friday discounts
    - Restores original discount_percent
    - Sets flag.is_active = False
    """
```

#### 2. Product Management Tasks
**SetLimitedProduct.py**
```python
@shared_task
def set_limited_products():
    """
    - Marks products as limited based on PRODUCT_LIMITATION flag
    - Updates badge to "Limited"
    - Sets is_limited = True
    """
```

**UnsetLimitedProduct.py**
```python
@shared_task
def unset_limited_products():
    """
    - Removes limited status
    - Reverts badge
    - Sets is_limited = False
    """
```

**BadgeUpdate.py**
```python
@shared_task
def update_product_badges():
    """
    - Updates product badges based on criteria
    - Examples: "New", "Hot", "Sale", "Limited"
    """
```

#### 3. Email Tasks (utils/Tasks/Emails/)
```
- EmailForBlackFriday.py
- EmailForLimitedProducts.py
- EmailForFreeShipping.py
- EmailForRefferralDiscount.py
- EmailForProductAds.py
```

### Running Celery

#### Development
```bash
# Start Celery worker
celery -A backend worker -l info

# Start Celery beat (for scheduled tasks)
celery -A backend beat -l info

# Combined
celery -A backend worker -B -l info
```

#### Production
```bash
# With concurrency
celery -A backend worker -l info --concurrency=4

# With specific queues
celery -A backend worker -Q high_priority,default -l info
```

### Task Scheduling (Celery Beat)
Scheduled tasks can be configured in `backend/settings/base.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'apply-black-friday-discount': {
        'task': 'utils.Tasks.ApplyBlackFridayDiscount.apply_friday_discount',
        'schedule': crontab(day_of_week=5, hour=0, minute=0),  # Every Friday at midnight
    },
    'reset-black-friday-discount': {
        'task': 'utils.Tasks.ResetBlackFridayDiscount.reset_friday_discount',
        'schedule': crontab(day_of_week=0, hour=23, minute=59),  # Sunday night
    },
}
```

---

## 8. Redis & Caching

### Redis Configuration (backend/settings/base.py)

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv('REDIS_PORT'),  # e.g., redis://localhost:6379/1
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,  # Fail gracefully if Redis is down
        }
    }
}
```

### Cache Keys (utils/enum.py)

```python
class CacheKeys(Enum):
    # User-related
    USER_PROFILE = "user_profile_{user_id}"
    USER_CART = "user_cart_{user_id}"
    USER_WATCHLIST = "user_watchlist_{user_id}"
    USER_WATCHLISTCART = "user_watchlist_cart_{user_id}"

    # Product-related
    PRODUCT_LIST = "product_list_all"
    PRODUCT_DETAIL = "product_detail_{product_id}"

    # Order-related
    ORDER_DETAIL = "order_detail_{user_id}_{order_id}"
    USER_ORDERS = "user_orders_{user_id}"
    USER_ORDER_TRACKING = "user_order_tracking_{user_id}_{order_id}"

    # Misc
    LOOKUP = "lookup"
    CUSTOMER_FEEDBACK_LIST = "customer_feedback_list"
    FEATURE_FLAGS = "feature_flag_{feature_name}"
    BANNER = "banner_{category}"

    @classmethod
    def format(cls, key, **kwargs):
        """Helper to format cache keys"""
        return key.value.format(**kwargs)
```

### Cache Manager (utils/cache_manager.py)

**Common patterns:**
```python
from django.core.cache import cache
from utils.enum import CacheKeys

# Set cache
cache_key = CacheKeys.format(CacheKeys.PRODUCT_DETAIL, product_id=123)
cache.set(cache_key, product_data, timeout=3600)  # 1 hour

# Get cache
data = cache.get(cache_key)

# Delete cache
cache.delete(cache_key)

# Pattern delete (delete multiple related keys)
cache.delete_pattern("product_*")
```

### Caching Strategy by Data Type

#### 1. Products
```python
# List cache (all products)
- Key: "product_list_all"
- Timeout: 30 minutes
- Invalidate: On product create/update/delete

# Detail cache (single product)
- Key: "product_detail_{product_id}"
- Timeout: 1 hour
- Invalidate: On product update
```

#### 2. User Data
```python
# Cart cache
- Key: "user_cart_{user_id}"
- Timeout: 15 minutes
- Invalidate: On cart item add/remove/update

# Watchlist cache
- Key: "user_watchlist_{user_id}"
- Timeout: 30 minutes
- Invalidate: On watchlist add/remove
```

#### 3. Feature Flags
```python
# Feature flag cache (in Cart model)
- Cached per instance in _cached_flags
- Lifetime: Request duration
- Avoids multiple DB queries per request
```

#### 4. Static Data
```python
# Lookups (categories, etc.)
- Key: "lookup"
- Timeout: 24 hours
- Invalidate: Rarely (on admin update)
```

### Cache Invalidation Patterns

#### Manual Invalidation
```python
from django.core.cache import cache

def update_product(product_id, data):
    # Update product
    product.update(**data)
    
    # Invalidate caches
    cache.delete(f"product_detail_{product_id}")
    cache.delete("product_list_all")
```

#### Signal-Based Invalidation
```python
# apps/aso/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    cache.delete(f"product_detail_{instance.id}")
    cache.delete("product_list_all")
```

### Redis as Celery Broker
```python
# Stores task messages
CELERY_BROKER_URL = os.getenv('REDIS_PORT')

# Stores task results
CELERY_RESULT_BACKEND = os.getenv('REDIS_PORT')
```

---

## 9. API Routes & Endpoints

### Root URLs (backend/urls.py)

```python
Main Routes:
- / → Redirects to /backdoor/
- /backdoor/ → Django Admin
- /admins/api/ → Administrator endpoints
- /aso/api/ → E-commerce endpoints
- /auth/api/ → Authentication endpoints
- /rider/api/ → Rider/delivery endpoints
- /health/ → Health check endpoints
- /doc/swagger/ → API documentation
- /doc/redoc/ → Alternative API docs
```

### Admin API (apps/administrator/urls.py)

```
Base: /admins/api/admin/

Authentication & Users:
POST   /admins/api/admin/login/                        # Admin login
POST   /admins/api/admin/send-token/                   # Resend OTP
POST   /admins/api/admin/change-password/              # Reset password

Dashboard:
GET    /admins/api/admin/dashboard/                    # Dashboard stats

Products:
GET    /admins/api/admin/products/                     # List products
POST   /admins/api/admin/products/                     # Create product
PUT    /admins/api/admin/products/                     # Update product
DELETE /admins/api/admin/products/                     # Delete product
POST   /admins/api/admin/bulk-update-badges/           # Bulk update badges
POST   /admins/api/admin/import-products/              # Bulk import
POST   /admins/api/admin/activate-products/            # Activate products

Orders:
GET    /admins/api/admin/orders/                       # List orders
# PUT    /admins/api/admin/update-order/               # Update order status

Customers:
GET    /admins/api/admin/customers/                    # List customers

Banners:
GET    /admins/api/admin/banners/                      # List all banners
GET    /admins/api/admin/banners/{category}/           # Banners by category
POST   /admins/api/admin/banners/                      # Create banner
PUT    /admins/api/admin/banners/                      # Update banner
DELETE /admins/api/admin/banners/                      # Delete banner

Feedback:
GET    /admins/api/admin/feedbacks/                    # List feedback
POST   /admins/api/admin/create/feedback/              # Create feedback
POST   /admins/api/admin/feedbacks/{pk}/mark_done/     # Mark as done

Transactions:
GET    /admins/api/admin/transactions/                 # List transactions

Feature Flags:
GET    /admins/api/admin/feature-flags/                # List feature flags
POST   /admins/api/admin/feature-flags/                # Create flag
PUT    /admins/api/admin/feature-flags/                # Update flag

Testing:
POST   /admins/api/admin/def-testing/                  # Testing endpoint
```

### Analytics API (apps/administrator/analytics_views.py)

```
Base: /admins/api/analytics/

Revenue & Sales:
GET    /admins/api/analytics/revenue/                  # Revenue over time
GET    /admins/api/analytics/orders/daily/             # Orders per day
GET    /admins/api/analytics/categories/sales/         # Sales by category
GET    /admins/api/analytics/products/top/             # Top products

Customer Analytics:
GET    /admins/api/analytics/customers/insights/       # Customer insights
GET    /admins/api/analytics/customers/top-buyers/     # Top buyers
GET    /admins/api/analytics/customers/locations/      # Customer locations
GET    /admins/api/analytics/customers/metrics/        # Customer metrics

Product Analytics:
GET    /admins/api/analytics/products/viewed/          # Most viewed
GET    /admins/api/analytics/products/rated/           # Top rated

Fulfillment:
GET    /admins/api/analytics/orders/fulfillment/       # Fulfillment stats
```

### E-commerce API (apps/aso/urls.py)

```
Base: /aso/api/product/

Products:
GET    /aso/api/product/                               # List products
        Query params: ?category=X&search=Y&page=N
GET    /aso/api/product/{id}/                          # Product detail
GET    /aso/api/product/lookups/                       # Category lookups
GET    /aso/api/product/limited-products/              # Limited products

Watchlist:
GET    /aso/api/product/watchlist-products/            # User watchlist
POST   /aso/api/product/toggle-watchlist/{product_id}/ # Add/remove watchlist
POST   /aso/api/product/remove-all-watchlist/          # Clear watchlist
POST   /aso/api/product/move-all-to-cart/              # Move all to cart

Cart:
GET    /aso/api/product/cart/                          # Get cart details
POST   /aso/api/product/add-to-cart/                   # Add item to cart
        Body: {product_id, quantity, desc: {color, size}}
PUT    /aso/api/product/cart/update-quantity/          # Update item quantity
        Body: {product_id, quantity}
PUT    /aso/api/product/cart/update-desc/              # Update item desc
        Body: {product_id, desc}
DELETE /aso/api/product/cart/remove-item/              # Remove cart item
        Body: {product_id}
PUT    /aso/api/product/cart/update-state/             # Update cart state
        Body: {state}
DELETE /aso/api/product/cart/clear/                    # Clear cart

Orders:
GET    /aso/api/product/lists/                         # User order list
GET    /aso/api/product/order-details/{pk}/            # Order details
POST   /aso/api/product/place-orders/                  # Place order
        Body: {shipping_address, payment_method}
POST   /aso/api/product/cart/reorder/                  # Reorder items
        Body: {order_id}

Payment:
GET    /aso/api/product/paystack-confirm-subscription/{reference}/
                                                        # Confirm payment

Tracking:
GET    /aso/api/product/track-order/{order_id}/        # Track order

Delivery:
GET    /aso/api/product/delivery-fees/                 # Delivery fee list

Feature Flags:
GET    /aso/api/product/feature-flag/{feature_name}/   # Check feature flag
        Returns: {enabled: true/false}

Misc:
GET    /aso/api/product/watchlist-and-cart-count/      # Counts
        Returns: {watchlist_count, cart_count}
```

### Authentication API (apps/users/urls.py)

```
Base: /auth/api/user/

Authentication:
POST   /auth/api/user/magic-login/                     # Request magic link
        Body: {email}
GET    /auth/api/user/verify/magic/login/{uidb64}/{token}/{url_email}/
                                                        # Verify magic login
POST   /auth/api/user/resend-link/                     # Resend verification

Email Verification:
GET    /auth/api/user/verify/email/{uidb64}/{token}/{url_email}/
                                                        # Verify email

Profile:
GET    /auth/api/user/profile/                         # Get user profile
PUT    /auth/api/user/update/profile/                  # Update profile
        Body: {first_name, last_name, phone, etc.}

Referral:
GET    /auth/api/user/referral/validate/{referral_code}/
                                                        # Validate referral code
```

### Rider API (apps/rider/urls.py)

```
Base: /rider/api/

[Rider-specific endpoints would be documented here]
```

### Health Check (django-health-check)

```
GET    /health/                                         # Overall health
       Returns: HTTP 200 if healthy, 500 if issues

Components checked:
- Database connectivity
- Cache (Redis) connectivity
- Media storage accessibility
```

### API Response Format

#### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

#### Error Response (DRF Standardized Errors)
```json
{
  "type": "validation_error",
  "errors": [
    {
      "code": "required",
      "detail": "This field is required.",
      "attr": "email"
    }
  ]
}
```

---

## 10. Authentication & Authorization

### Authentication Method

**JWT (JSON Web Token) Authentication** via `djangorestframework-simplejwt`

### JWT Configuration (backend/settings/base.py)

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}
```

### Authentication Flow

#### 1. Magic Link Authentication
```
User enters email
    ↓
System generates magic link
    ↓
Email sent with link
    ↓
User clicks link
    ↓
Token verified
    ↓
JWT tokens issued
    ↓
User authenticated
```

**Endpoints:**
```python
POST /auth/api/user/magic-login/
Body: {"email": "user@example.com"}

GET /auth/api/user/verify/magic/login/{uidb64}/{token}/{url_email}/
Returns: {"access": "...", "refresh": "..."}
```

#### 2. Admin Login
```python
POST /admins/api/admin/login/
Body: {
    "email": "admin@example.com",
    "password": "secure_password"
}
Returns: {
    "access": "eyJ...",
    "refresh": "eyJ...",
    "user": {...}
}
```

### User Groups (utils/enum.py)

```python
class GroupNames(Enum):
    ADMIN = "Admin"
    CUSTOMER = "Customer"
    RIDER = "Rider"
```

### Custom Permissions (utils/permissions.py)

```python
# Example permission classes
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name=GroupNames.ADMIN.value).exists()

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name=GroupNames.CUSTOMER.value).exists()
```

### Using Authentication in Views

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        # Access authenticated user
        return Response({"message": f"Hello {user.email}"})
```

### Token Usage

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Refresh

```python
POST /api/token/refresh/
Body: {"refresh": "eyJ..."}
Returns: {"access": "eyJ..."}
```

### Thread-Local Current User (utils/Middlewares/threadlocals.py)

Stores current user in thread-local storage for access anywhere:

```python
from utils.Middlewares.threadlocals import get_current_user

user = get_current_user()
```

---

## 11. Middleware

### Custom Middleware Stack

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'utils.Middlewares.log_exceptions.ExceptionLoggingMiddleware',  # Custom
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'utils.Middlewares.threadlocals.CurrentUserMiddleware',  # Custom
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 1. ExceptionLoggingMiddleware
**Location:** `utils/Middlewares/log_exceptions.py`

**Purpose:** Logs all exceptions with full traceback before they're processed by Django's error handler.

**Features:**
- Captures exception details
- Logs to file (logs/app.log)
- Sends email to admins on production errors
- Includes request context (path, method, user)

### 2. CurrentUserMiddleware
**Location:** `utils/Middlewares/threadlocals.py`

**Purpose:** Makes current user accessible via thread-local storage.

**Usage:**
```python
from utils.Middlewares.threadlocals import get_current_user

user = get_current_user()
if user.is_authenticated:
    # Do something with user
    pass
```

**Use Cases:**
- Automatic created_by/updated_by fields
- Audit logging
- Permission checks in utility functions

### CORS Middleware
**Package:** `django-cors-headers`

**Configuration:**
```python
CORS_ALLOW_ALL_ORIGINS = True  # Development only!
# Production should use CORS_ALLOWED_ORIGINS
```

---

## 12. Settings Configuration

### Settings Structure

```
backend/settings/
├── __init__.py           # Environment detection
├── base.py               # Base settings (shared)
├── dev.py                # Development overrides
├── prod.py               # Production settings
└── staging.py            # Staging settings
```

### Environment Variables (.env)

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=backend.settings.dev

# Database
DB_NAME=aso_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_PORT=redis://localhost:6379/1

# URLs
BASE_URL=http://localhost:3000
BACKEND_BASE_URL=http://localhost:8000

# Payment
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxxxxx

# Security
SECURE=False

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### Base Settings Highlights

#### Installed Apps
```python
SYSTEM_DEFINE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... standard Django apps
]

APPLICATION_APPS = [
    'apps.administrator',
    'apps.aso',
    'apps.users',
    'apps.rider',
]

THIRD_PARTIES_APPS = [
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'drf_yasg',
    'django_filters',
    'health_check',
]
```

#### REST Framework
```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 21,
    "DEFAULT_THROTTLE_RATES": {
        'user': '20000/hour',
        'anon': '20000/hour',
        "magic_link": "50/minute",
    },
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
}
```

#### Static & Media Files
```python
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

#### Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'app.log'),
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
}
```

### Environment-Specific Settings

#### Development (dev.py)
```python
DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

#### Production (prod.py)
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 13. Docker Setup

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Run entrypoint
CMD ["/entrypoint.sh"]
```

### docker-compose.yml

```yaml
version: '3.9'

services:
  web:
    build: .
    container_name: django_app
    command: /entrypoint.sh
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    restart: always

  db:
    image: postgres:15
    container_name: postgres_db
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}

volumes:
  postgres_data:
```

### entrypoint.sh

```bash
#!/bin/bash

# Wait for database
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py createsuperuser --noinput || true

# Collect static files
python manage.py collectstatic --noinput

# Start server
python manage.py runserver 0.0.0.0:8000
```

### Docker Commands

```bash
# Build images
docker-compose build

# Start containers
docker-compose up

# Start in background
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web pytest
```

---

## 14. Testing

### Test Configuration (pytest.ini)

```ini
[pytest]
DJANGO_SETTINGS_MODULE = backend.test_settings
python_files = tests.py test_*.py *_tests.py
addopts = -v --tb=short
```

### Test Structure

```
apps/
├── administrator/
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_views.py
│       └── test_analytics.py
├── aso/
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_cart.py
│       ├── test_orders.py
│       └── test_feature_flags.py
└── users/
    └── tests/
        ├── __init__.py
        ├── test_authentication.py
        └── test_profile.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific app tests
pytest apps/aso/tests/

# Run specific test file
pytest apps/aso/tests/test_models.py

# Run specific test
pytest apps/aso/tests/test_models.py::TestProductModel::test_discount_calculation

# Run with coverage
pytest --cov=apps --cov-report=html

# Run parallel
pytest -n auto
```

### Test Settings (backend/test_settings.py)

```python
# Inherit from base settings
from .settings.base import *

# Override for testing
DEBUG = False

# Use in-memory database for speed
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Simple password hasher for speed
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
```

### Writing Tests

#### Model Test Example
```python
import pytest
from apps.aso.models import Product, Cart, CartItem
from apps.users.models import User

@pytest.mark.django_db
class TestCartModel:
    def test_cart_subtotal(self):
        user = User.objects.create(email="test@example.com")
        cart = Cart.objects.create(user=user)
        product = Product.objects.create(
            title="Test Product",
            original_price=100.00,
            current_price=100.00
        )
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        
        assert cart.subtotal() == 200.00
```

#### View Test Example
```python
import pytest
from rest_framework.test import APIClient
from apps.users.models import User

@pytest.mark.django_db
class TestProductListView:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create(email="test@example.com")
        
    def test_list_products(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/aso/api/product/')
        
        assert response.status_code == 200
        assert 'results' in response.data
```

---

## 15. Logging

### Log Configuration

**Log Directory:** `logs/`
**Log File:** `logs/app.log`

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages (logged to file)
- **CRITICAL**: Critical errors

### Logging in Code

```python
import logging

logger = logging.getLogger(__name__)

# Different log levels
logger.debug("Debugging information")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)  # Includes traceback
logger.critical("Critical error")
```

### Request Logging

Automatically logged by `ExceptionLoggingMiddleware`:
- Request path
- Request method
- User (if authenticated)
- Exception details
- Full traceback

### Celery Task Logging

```python
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def my_task():
    logger.info("Task started")
    # Task logic
    logger.info("Task completed")
```

### Log Helpers (utils/log_helpers.py)

```python
from utils.log_helpers import log_error, log_warning

# Quick logging functions
log_error("Something went wrong", extra_data={"user_id": 123})
log_warning("This looks suspicious", context={"ip": "1.2.3.4"})
```

---

## 16. Best Practices

### Database Optimization

#### 1. Use select_related() and prefetch_related()
```python
# Bad: N+1 query problem
orders = Order.objects.all()
for order in orders:
    print(order.user.email)  # Separate query for each user

# Good: Single query with join
orders = Order.objects.select_related('user').all()
for order in orders:
    print(order.user.email)

# Good: Prefetch many-to-many
products = Product.objects.prefetch_related('category', 'colors', 'sizes').all()
```

#### 2. Use only() and defer()
```python
# Only fetch needed fields
products = Product.objects.only('id', 'title', 'current_price')

# Defer large fields
products = Product.objects.defer('description')
```

#### 3. Use indexes
```python
class Meta:
    indexes = [
        models.Index(fields=['created_at']),
        models.Index(fields=['user', 'status']),
    ]
```

### Caching Strategy

#### 1. Cache expensive queries
```python
from django.core.cache import cache

def get_products():
    products = cache.get('product_list')
    if products is None:
        products = list(Product.objects.all())
        cache.set('product_list', products, 1800)  # 30 minutes
    return products
```

#### 2. Invalidate cache on updates
```python
@receiver(post_save, sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    cache.delete('product_list')
    cache.delete(f'product_{instance.id}')
```

### API Best Practices

#### 1. Use serializers for validation
```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        
    def validate_discount_percent(self, value):
        if value < 0 or value > 100:
            raise ValidationError("Discount must be between 0 and 100")
        return value
```

#### 2. Paginate large result sets
```python
# Automatically handled by REST_FRAMEWORK settings
# PAGE_SIZE = 21
```

#### 3. Filter and search
```python
from django_filters import rest_framework as filters

class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = ['category', 'badge']
```

### Security Best Practices

#### 1. Never commit sensitive data
```python
# Use environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
```

#### 2. Validate user input
```python
from rest_framework import serializers

class OrderSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, max_value=100)
```

#### 3. Use permissions
```python
class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
```

### Feature Flag Best Practices

#### 1. Always check feature flags
```python
# Don't assume a feature is enabled
flag, enabled = is_feature_enabled(FeatureNames.BLACK_FRIDAY.value)
if enabled:
    apply_discount()
```

#### 2. Use feature flags for gradual rollouts
```python
# Enable for specific users first
flag = FeatureFlag.objects.get(name="New Feature")
flag.users.add(beta_user)
```

#### 3. Clean up old flags
```python
# Remove flags for fully deployed features
# Archive flags for retired features
```

### Code Organization

#### 1. Use Business Logic Layer (BLL)
```python
# apps/aso/BBL/Commands/CreateOrderCommand.py
class CreateOrderCommand:
    def execute(self, cart, shipping_address):
        # Complex order creation logic
        pass
```

#### 2. Keep views thin
```python
class PlaceOrderView(APIView):
    def post(self, request):
        command = CreateOrderCommand()
        order = command.execute(request.user.cart, request.data)
        return Response(OrderSerializer(order).data)
```

#### 3. Use signals for side effects
```python
@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
    if created:
        send_email_task.delay(instance.id)
```

---

## Quick Reference

### Common Commands

```bash
# Development server
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell

# Celery worker
celery -A backend worker -l info

# Run tests
pytest

# Check for issues
python manage.py check
```

### Important URLs (Development)

```
Admin: http://localhost:8000/backdoor/
API Docs: http://localhost:8000/doc/swagger/
Health Check: http://localhost:8000/health/
```

### Environment Variables Quick Reference

```env
SECRET_KEY=              # Django secret key
DEBUG=True               # Debug mode
DB_NAME=                 # Database name
DB_USER=                 # Database user
DB_PASSWORD=             # Database password
REDIS_PORT=              # Redis connection URL
PAYSTACK_SECRET_KEY=     # Payment gateway key
BASE_URL=                # Frontend URL
BACKEND_BASE_URL=        # Backend URL
```

---

## Troubleshooting

### Common Issues

#### 1. Celery tasks not running
```bash
# Check if Redis is running
redis-cli ping

# Restart Celery worker
celery -A backend worker -l info

# Check task status
python manage.py shell
>>> from celery import current_app
>>> i = current_app.control.inspect()
>>> i.active()
```

#### 2. Cache not working
```bash
# Check Redis connection
redis-cli ping

# Clear cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

#### 3. Database migrations fail
```bash
# Reset migrations (development only!)
python manage.py migrate --fake app_name zero
python manage.py migrate app_name

# Or delete migration files and regenerate
```

#### 4. Static files not loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT setting
```

---

## Conclusion

This documentation provides a comprehensive overview of the E-Sell Backend project. For specific implementation details, refer to the source code or contact the development team.

**Remember to:**
- Keep this documentation updated as the project evolves
- Document new features and changes
- Share knowledge with team members
- Follow best practices and coding standards

---

**Last Updated:** November 12, 2025  
**Maintainer:** itopa1999  
**Repository:** e_aso_backend
