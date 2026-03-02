from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Cart, CartItem, FeatureFlag, Order, OrderFeedBack, OrderItem, OrderReturn, 
    OrderTracking, PaymentDetail, Product, ProductColor, ProductSize, 
    ProductDetail, ProductImage, LookUp, ShippingAddress, WatchList, RecentSearch, Notification
)


# ==================== INLINES ====================

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    readonly_fields = ("product",)
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    readonly_fields = ("product",)
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class ProductDetailInline(admin.StackedInline):
    model = ProductDetail
    extra = 1
    readonly_fields = ("product",)
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("product",)
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    readonly_fields = ("cart", "product", "quantity", "desc")
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("order", "product", "quantity", "price", "desc")
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class TrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 1
    readonly_fields = ("order",)
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class ShippingAddressItemInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0
    readonly_fields = ("order",)
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class PaymentDetailInline(admin.TabularInline):
    model = PaymentDetail
    extra = 0
    readonly_fields = ("order",)
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class OrderFeedBackInline(admin.TabularInline):
    model = OrderFeedBack
    extra = 0
    readonly_fields = ("order",)
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


class OrderReturnInline(admin.StackedInline):
    model = OrderReturn
    extra = 0
    readonly_fields = ("order",)
    exclude = ("created_at", "created_by", "modified_by", "is_deleted", "deleted_at", "deleted_by")


# ==================== ADMIN CLASSES ====================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_number", "title", "badge_display", "price_display", "rating", "reviews_count", "status_display", "created_at")
    list_display_links = ("product_number", "title")
    search_fields = ("title", "product_number", "description")
    list_filter = ("badge", "display_product", "is_limited", "created_at", "category")
    readonly_fields = ("product_number", "current_price", "created_at", "modified_at")
    filter_horizontal = ("category",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Basic Information", {
            "fields": ("product_number", "title", "badge", "category", "description")
        }),
        ("Pricing", {
            "fields": ("original_price", "current_price", "discount_percent")
        }),
        ("Product Details", {
            "fields": ("rating", "reviews_count", "main_image", "display_product", "is_limited")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    inlines = [ProductColorInline, ProductSizeInline, ProductDetailInline, ProductImageInline]

    def badge_display(self, obj):
        colors = {
            "New": "blue",
            "Sale": "red",
            "Hot": "orange",
            "Limited": "purple",
        }
        color = colors.get(obj.badge, "gray")
        return format_html(f'<span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 3px;">{obj.badge}</span>')
    badge_display.short_description = "Badge"

    def price_display(self, obj):
        if obj.discount_percent:
            return format_html(
                '<span style="color: red; font-weight: bold;">₦{}</span> <span style="text-decoration: line-through; color: gray;">₦{}</span> <span style="color: green;">(-{}%)</span>',
                obj.current_price, obj.original_price, obj.discount_percent
            )
        return format_html('<span style="font-weight: bold;">₦{}</span>', obj.current_price)
    price_display.short_description = "Price"

    def status_display(self, obj):
        if obj.display_product:
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Hidden')
    status_display.short_description = "Status"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "state", "items_count", "subtotal_display", "created_at", "modified_at")
    list_display_links = ("user",)
    search_fields = ("user__email", "user__first_name", "user__last_name", "state")
    list_filter = ("state", "created_at")
    readonly_fields = ("user", "created_at", "modified_at")
    ordering = ("-modified_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Cart Information", {
            "fields": ("user", "state")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    inlines = [CartItemInline]

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Items"

    def subtotal_display(self, obj):
        return format_html('<span style="font-weight: bold;">₦{}</span>', obj.subtotal())
    subtotal_display.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "tracking_number", "total_display", "current_status", "payment_status_display", "payment_method_display", "dispatcher", "created_at")
    list_display_links = ("order_number", "user")
    search_fields = ("order_number", "tracking_number", "payment_reference", "user__email", "user__first_name", "user__last_name")
    list_filter = ("carrier", "payment_status", "payment_method", "created_at", "estimated_delivery_date")
    readonly_fields = ("order_number", "tracking_number", "subtotal", "shipping_fee", "discount", "total", "estimated_delivery_date", "user", "payment_reference", "created_at", "modified_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50
    autocomplete_fields = ["dispatcher"]

    fieldsets = (
        ("Order Information", {
            "fields": ("order_number", "tracking_number", "carrier", "user")
        }),
        ("Financial Summary", {
            "fields": ("subtotal", "shipping_fee", "discount", "total")
        }),
        ("Payment Information", {
            "fields": ("payment_status", "payment_method", "payment_reference")
        }),
        ("Delivery Information", {
            "fields": ("dispatcher", "delivery_date", "estimated_delivery_date")
        }),
        ("Additional Information", {
            "fields": ("other_info",)
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    inlines = [OrderItemInline, TrackingInline, ShippingAddressItemInline, PaymentDetailInline, OrderFeedBackInline, OrderReturnInline]

    def total_display(self, obj):
        return format_html('<span style="font-weight: bold; color: green;">₦{}</span>', obj.total)
    total_display.short_description = "Total"

    def current_status(self, obj):
        latest = obj.tracking_events.order_by("-date").first()
        if latest:
            colors = {
                "placed": "blue",
                "processing": "orange",
                "shipped": "purple",
                "in_transit": "teal",
                "delivered": "green",
                "cancelled": "red",
            }
            color = colors.get(latest.status, "gray")
            return format_html(f'<span style="color: {color};">●</span> {latest.get_status_display()}')
        return format_html('<span style="color: gray;">●</span> Unknown')
    current_status.short_description = "Status"

    def payment_status_display(self, obj):
        colors = {
            "pending": "orange",
            "confirmed": "green",
            "failed": "red",
            "cancelled": "gray",
        }
        color = colors.get(obj.payment_status, "gray")
        return format_html(f'<span style="color: {color}; font-weight: bold;">●</span> {obj.payment_status.upper()}')
    payment_status_display.short_description = "Payment Status"

    def payment_method_display(self, obj):
        method_icons = {
            "paystack": "💳 Paystack",
            "flutterwave": "🌊 Flutterwave",
            "monnify": "💰 Monnify",
        }
        return method_icons.get(obj.payment_method, obj.payment_method)
    payment_method_display.short_description = "Payment Method"


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_display_links = ("user", "product")
    search_fields = ("user__email", "user__first_name", "product__title")
    list_filter = ("created_at",)
    readonly_fields = ("user", "created_at", "modified_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Watchlist Information", {
            "fields": ("product", "user")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )


@admin.register(RecentSearch)
class RecentSearchAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_display_links = ("user", "product")
    search_fields = ("user__email", "user__first_name", "product__title")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "modified_at", "user")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Recent Search Information", {
            "fields": ("product", "user")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set user on creation, not on update
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(LookUp)
class LookUpAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "description_preview", "created_at")
    list_display_links = ("name",)
    search_fields = ("name", "category", "description")
    list_filter = ("category", "created_at")
    readonly_fields = ("created_at", "modified_at")
    ordering = ("name",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Lookup Information", {
            "fields": ("name", "category", "description")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def description_preview(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_preview.short_description = "Description"


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("name", "enabled_status", "is_active", "start_date", "end_date", "discount_percent", "created_at", "modified_at")
    list_display_links = ("name",)
    search_fields = ("name", "description")
    list_filter = ("is_enabled", "is_active", "name", "start_date", "end_date")
    readonly_fields = ("created_at", "modified_at")
    filter_horizontal = ("users",)
    ordering = ("name",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Feature Information", {
            "fields": ("name", "description", "is_enabled", "is_active")
        }),
        ("Configuration", {
            "fields": ("users", "start_date", "end_date", "discount_percent", "count")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def enabled_status(self, obj):
        if obj.is_enabled:
            return format_html('<span style="color: green;">✓</span> Enabled')
        return format_html('<span style="color: red;">✗</span> Disabled')
    enabled_status.short_description = "Status"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user_email", "title", "type", "is_read", "created_at")
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("user__email", "title", "message")
    readonly_fields = ("id", "created_at", "modified_at", "created_by", "modified_by", "deleted_at", "deleted_by")
    
    fieldsets = (
        ("Notification Information", {
            "fields": ("user", "title", "message", "type", "action_url")
        }),
        ("Status", {
            "fields": ("is_read",)
        }),
        ("Base Model Info", {
            "fields": ("id", "created_at", "modified_at", "created_by", "modified_by", "deleted_at", "deleted_by"),
            "classes": ("collapse",)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"