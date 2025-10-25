from django.contrib import admin

from apps.administrator.models import Banner
from utils.base_admin import BaseAdmin

@admin.register(Banner)
class LookUpAdmin(BaseAdmin):
    custom_fieldsets  = (
        ("Information", {
            "fields": ("title", "image", "category", "link", "created_at")
        }),
    )