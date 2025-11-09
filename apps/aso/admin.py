from django.contrib import admin

from utils.base_admin import BaseAdmin
from .models import (
    Cart, CartItem, FeatureFlag, Order, OrderFeedBack, OrderItem, OrderReturn, 
    OrderTracking, PaymentDetail, Product, ProductColor, ProductSize, 
    ProductDetail, ProductImage, LookUp, ShippingAddress, WatchList
)

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class ProductDetailInline(admin.StackedInline):
    model = ProductDetail
    extra = 1
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


@admin.register(Product)
class ProductAdmin(BaseAdmin):
    custom_fieldsets  = (
        ("Information", {
            "fields": ('title', 'badge',
                       'category', 'created_at',
                       'description','current_price', 'original_price',
                       'discount_percent','rating','reviews_count', 'main_image',
                       'display_product', 'is_limited')
        }),
    )
    search_fields = ('title',)
    list_filter = ('badge', 'created_at', 'category')
    # prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('category',)

    inlines = [
        ProductColorInline,
        ProductSizeInline,
        ProductDetailInline,
        ProductImageInline
    ]
    
    
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


@admin.register(Cart)
class CartAdmin(BaseAdmin):
    inlines = [CartItemInline]
    list_display = ['user', 'created_at', 'modified_at']
    
    

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")

class TrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 1
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")

class ShippingAddressItemInline(admin.TabularInline):
    model = ShippingAddress
    extra = 0
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class PaymentDetailInline(admin.TabularInline):
    model = PaymentDetail
    extra = 0
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class OrderFeedBackInline(admin.TabularInline):
    model = OrderFeedBack
    extra = 0
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class OrderReturnInline(admin.TabularInline):
    model = OrderReturn
    extra = 0
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


@admin.register(Order)
class OrderAdmin(BaseAdmin):
    list_display = ['order_number', 'user', 'total', 'created_at']
    inlines = [
        OrderItemInline, 
        TrackingInline, 
        ShippingAddressItemInline, 
        PaymentDetailInline, 
        OrderFeedBackInline,
        OrderReturnInline
        ]



@admin.register(WatchList)
class WatchListAdmin(BaseAdmin):
    custom_fieldsets  = (
        ("Information", {
            "fields": ("product", "user")
        }),
    )


@admin.register(LookUp)
class LookUpAdmin(BaseAdmin):
    custom_fieldsets  = (
        ("Lookup Information", {
            "fields": ("name", "category", "description")
        }),
    )
    

@admin.register(FeatureFlag)
class FeatureFlagAdmin(BaseAdmin):
    list_display = ("name", "is_enabled", "created_at", "modified_at")
    search_fields = ("name", "description")
    list_filter = ("is_enabled",)
    filter_horizontal = ("users",)

    custom_fieldsets = (
        ("Feature Information", {
            "fields": ("name", "description", "is_enabled", "users", "start_date", "end_date", "discount_percent", "count", "is_active")
        }),
    )