from django.contrib import admin

from apps.administrator.models import Banner, CustomerFeedback
from utils.base_admin import BaseAdmin

@admin.register(Banner)
class BannerAdmin(BaseAdmin):
    custom_fieldsets  = (
        ("Information", {
            "fields": ("title", "image", "category", "link", "created_at")
        }),
    )
    

@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(BaseAdmin):
    custom_fieldsets = (
        ("Feedback Information", {
            "fields": ("user", "feedback", "rating", "is_done", "created_at")
        }),
    )