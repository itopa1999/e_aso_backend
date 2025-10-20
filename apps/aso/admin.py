from django.contrib import admin

from utils.base_admin import BaseAdmin
from .models import (
    Cart, CartItem, Order, OrderFeedBack, OrderItem, OrderReturn, 
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
    list_display = ('title', 'current_price', 'badge', 'category_names', 'created_at')
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