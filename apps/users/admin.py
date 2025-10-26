from django.contrib import admin

from utils.base_admin import BaseAdmin
from .models import *
# Register your models here.

@admin.register(User)
class UserAdmin(BaseAdmin):
    """Custom admin for User with BaseAdmin integration."""
    list_display = (
        "email", "first_name", "last_name",
        "phone", "rider_number", "is_active", "is_staff", "created_at"
    )
    search_fields = ("email", "first_name", "last_name", "phone", "rider_number")
    list_filter = ("is_active", "is_staff", "is_superuser", "created_at")
    readonly_fields = ("referral_code", "is_referral_qualified", "created_at", "modified_at")

    custom_fieldsets = (
        ("User Information", {
            "fields": (
                "email",
                "first_name",
                "last_name",
                "phone",
                "rider_number",
                "referral_code",
                "is_referral_qualified",
                "referral_used",
                "password",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
    )


@admin.register(UserVerification)
class UserVerificationAdmin(BaseAdmin):
    """Admin for user verification management."""
    list_display = ("user", "token", "is_verified", "created_at")
    search_fields = ("user__email", "token")
    list_filter = ("is_verified", "created_at")

    custom_fieldsets = (
        ("Verification Info", {
            "fields": (
                "user",
                "token",
                "is_verified",
            ),
        }),
    )
    
    
@admin.register(Referral)
class LookUpAdmin(BaseAdmin):
    custom_fieldsets  = (
        ("Lookup Information", {
            "fields": ("referrer", "referee", "successful", "created_at")
        }),
    )