from django.contrib import admin
from django.utils.html import format_html
from apps.administrator.models import Banner, CustomerFeedback


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "image_preview", "link_display", "created_at")
    list_display_links = ("title",)
    search_fields = ("title", "category", "link")
    list_filter = ("category", "created_at")
    readonly_fields = ("image_preview", "created_at", "modified_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Banner Information", {
            "fields": ("title", "category", "image", "image_preview", "link")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 100px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"

    def link_display(self, obj):
        if obj.link:
            return format_html('<a href="{}" target="_blank">View Link</a>', obj.link)
        return "-"
    link_display.short_description = "Link"


@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "rating_display", "feedback_preview", "status_display", "created_at")
    list_display_links = ("user",)
    search_fields = ("user", "feedback")
    list_filter = ("rating", "is_done", "created_at")
    readonly_fields = ("created_at", "modified_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Feedback Information", {
            "fields": ("user", "rating", "feedback", "is_done")
        }),
        ("Base Model Info", {
            "fields": ("created_at", "modified_at", "deleted_at", "created_by", "modified_by", "deleted_by"),
            "classes": ("collapse",)
        }),
    )

    def rating_display(self, obj):
        stars = "⭐" * obj.rating
        return format_html('<span style="color: gold;">{}</span> ({})', stars, obj.rating)
    rating_display.short_description = "Rating"

    def feedback_preview(self, obj):
        return obj.feedback[:50] + "..." if len(obj.feedback) > 50 else obj.feedback
    feedback_preview.short_description = "Feedback"

    def status_display(self, obj):
        if obj.is_done:
            return format_html('<span style="color: green;">✓</span> Completed')
        return format_html('<span style="color: orange;">⏳</span> Pending')
    status_display.short_description = "Status"