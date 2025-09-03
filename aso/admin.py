from django.contrib import admin
from .models import Cart, CartItem, Order, OrderFeedBack, OrderItem, OrderReturn, OrderTracking, PaymentDetail, Product, ProductColor, ProductSize, ProductDetail, ProductImage, Category, ShippingAddress, WatchList

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


class ProductDetailInline(admin.StackedInline):
    model = ProductDetail
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
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

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ['user', 'created_at', 'updated_at']
    
    

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class TrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 1
    

class ShippingAddressItemInline(admin.TabularInline):
    model = ShippingAddress
    extra = 0

class PaymentDetailInline(admin.TabularInline):
    model = PaymentDetail
    extra = 0
    
class OrderFeedBackInline(admin.TabularInline):
    model = OrderFeedBack
    extra = 0
    
class OrderReturnInline(admin.TabularInline):
    model = OrderReturn
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total', 'created_at']
    inlines = [
        OrderItemInline, 
        TrackingInline, 
        ShippingAddressItemInline, 
        PaymentDetailInline, 
        OrderFeedBackInline,
        OrderReturnInline
        ]



admin.site.register(WatchList)
admin.site.register(Category)