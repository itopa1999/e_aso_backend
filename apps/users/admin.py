from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Custom admin for User with admin.ModelAdmin integration."""
    list_display = (
        "email", "full_name_display", "phone", "rider_number", 
        "status_display", "referral_status_display", "telegram_notification_status", "created_at"
    )
    list_display_links = ("email", "full_name_display")
    search_fields = ("email", "first_name", "last_name", "phone", "rider_number", "referral_code", "telegram_user_id", "telegram_user_chat_id")
    list_filter = ("is_active", "is_staff", "is_superuser", "is_referral_qualified", "referral_used", "telegram_notifications_enabled", "created_at", "groups")
    readonly_fields = ("referral_code", "is_referral_qualified", "telegram_user_id", "date_joined", "last_login", "created_at", "modified_at")
    filter_horizontal = ("groups", "user_permissions")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Personal Information", {
            "fields": (
                "email",
                "first_name",
                "last_name",
                "phone",
                "rider_number",
            ),
        }),
        ("Referral Information", {
            "fields": (
                "referral_code",
                "is_referral_qualified",
                "referral_used",
                "referral_used_purchase",
            ),
        }),
        ("Telegram Notifications", {
            "fields": (
                "telegram_user_id",
                "telegram_user_chat_id",
                "telegram_notifications_enabled",
            ),
        }),
        ("Permissions & Access", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Password", {
            "fields": ("password",),
        }),
        ("Important Dates", {
            "fields": ("date_joined", "last_login"),
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name_display.short_description = "Full Name"

    def status_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Inactive')
    status_display.short_description = "Status"

    def referral_status_display(self, obj):
        if obj.is_referral_qualified:
            return format_html('<span style="color: green;">✓</span> Qualified')
        return format_html('<span style="color: gray;">✗</span> Not Qualified')
    referral_status_display.short_description = "Referral Status"

    def telegram_notification_status(self, obj):
        if obj.telegram_notifications_enabled:
            return format_html('<span style="color: green;">✓</span> Enabled')
        return format_html('<span style="color: gray;">✗</span> Disabled')
    telegram_notification_status.short_description = "Telegram Notifications"


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    """Admin for user verification management."""
    list_display = ("user", "token", "verification_status", "created_at", "is_expired")
    list_display_links = ("user", "token")
    search_fields = ("user__email", "user__first_name", "user__last_name", "token")
    list_filter = ("is_verified", "created_at")
    readonly_fields = ("created_at", "modified_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Verification Info", {
            "fields": (
                "user",
                "token",
                "is_verified",
            ),
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def verification_status(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓</span> Verified')
        return format_html('<span style="color: orange;">⏳</span> Pending')
    verification_status.short_description = "Status"

    def is_expired(self, obj):
        if obj.is_token_expired():
            return format_html('<span style="color: red;">●</span> Expired')
        return format_html('<span style="color: green;">●</span> Valid')
    is_expired.short_description = "Token Status"
    
    
@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    """Admin for referral management."""
    list_display = ("referrer", "referee", "successful_display", "created_at")
    list_display_links = ("referrer", "referee")
    search_fields = ("referrer__email", "referrer__first_name", "referee__email", "referee__first_name")
    list_filter = ("successful", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Referral Information", {
            "fields": ("referrer", "referee", "successful")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def successful_display(self, obj):
        if obj.successful:
            return format_html('<span style="color: green;">✓</span> Successful')
        return format_html('<span style="color: gray;">✗</span> Pending')
    successful_display.short_description = "Status"

    
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin for transaction management."""
    list_display = ("reference", "user", "amount", "transaction_type", "channel", "status_display", "created_at")
    list_display_links = ("reference", "user")
    search_fields = ("reference", "user__email", "user__first_name", "user__last_name", "order_id")
    list_filter = ("transaction_type", "channel", "status", "created_at")
    readonly_fields = ("reference", "created_at", "modified_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Transaction Information", {
            "fields": ("user", "amount", "transaction_type", "reference", "channel", "status", "order_id")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def status_display(self, obj):
        colors = {
            "success": "green",
            "pending": "orange",
            "failed": "red",
        }
        color = colors.get(obj.status.lower(), "gray")
        return format_html(f'<span style="color: {color};">●</span> {obj.status}')
    status_display.short_description = "Status"
    
    
@admin.register(ContactFormSubmission)
class ContactFormSubmissionAdmin(admin.ModelAdmin):
    """Admin for contact form submissions."""
    list_display = ("full_name", "email", "phone", "subject_preview", "status_display", "created_at")
    list_display_links = ("full_name", "email")
    search_fields = ("full_name", "email", "phone", "subject", "message")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at", "modified_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Contact Information", {
            "fields": ("full_name", "phone", "email")
        }),
        ("Message Details", {
            "fields": ("subject", "message", "status")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def subject_preview(self, obj):
        return obj.subject[:50] + "..." if len(obj.subject) > 50 else obj.subject
    subject_preview.short_description = "Subject"

    def status_display(self, obj):
        colors = {
            "new": "blue",
            "in_progress": "orange",
            "resolved": "green",
            "closed": "gray",
        }
        color = colors.get(obj.status.lower(), "gray")
        return format_html(f'<span style="color: {color};">●</span> {obj.status}')
    status_display.short_description = "Status"


@admin.register(UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    """Admin for user device and agent tracking."""
    list_display = ("user", "device_display", "browser_display", "os_display", "ip_address", "is_active_display", "last_seen")
    list_display_links = ("user", "device_display")
    search_fields = ("user__email", "user__first_name", "user__last_name", "ip_address", "browser", "os")
    list_filter = ("is_active", "device_type", "last_seen", "created_at")
    readonly_fields = ("user_agent_string", "created_at", "modified_at", 'last_seen')
    ordering = ("-last_seen",)
    date_hierarchy = "last_seen"
    list_per_page = 50

    fieldsets = (
        ("Device Information", {
            "fields": (
                "user",
                "device",
                "device_type",
            ),
        }),
        ("Browser Information", {
            "fields": (
                "browser",
                "browser_version",
            ),
        }),
        ("Operating System", {
            "fields": (
                "os",
                "os_version",
            ),
        }),
        ("Network Information", {
            "fields": (
                "ip_address",
                "user_agent_string",
            ),
        }),
        ("Status & Activity", {
            "fields": (
                "is_active",
                "last_seen",
            ),
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def device_display(self, obj):
        """Display device with icon."""
        device_icons = {
            "mobile": "📱",
            "tablet": "📱",
            "desktop": "🖥️",
        }
        icon = device_icons.get(obj.device_type, "❓")
        return f"{icon} {obj.device or 'Unknown'}"
    device_display.short_description = "Device"

    def browser_display(self, obj):
        """Display browser with version."""
        browser = obj.browser or "Unknown"
        version = obj.browser_version or ""
        return f"{browser} {version}".strip()
    browser_display.short_description = "Browser"

    def os_display(self, obj):
        """Display OS with version."""
        os_name = obj.os or "Unknown"
        version = obj.os_version or ""
        return f"{os_name} {version}".strip()
    os_display.short_description = "OS"

    def is_active_display(self, obj):
        """Display active status with color."""
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Inactive')
    is_active_display.short_description = "Status"
    