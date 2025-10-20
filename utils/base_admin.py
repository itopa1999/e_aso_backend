from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    """Base admin with collapsed meta fields."""
    readonly_fields = ("created_at", "modified_at")

    base_fieldset = (
        ("Data Information", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "created_by",
                "modified_by",
                "is_deleted",
                "deleted_at",
                "deleted_by",
            ),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        # Get fieldsets from subclass if defined
        fieldsets = getattr(self, "custom_fieldsets", None)
        if fieldsets:
            return fieldsets + self.base_fieldset
        # Otherwise, just show the base one
        return self.base_fieldset
