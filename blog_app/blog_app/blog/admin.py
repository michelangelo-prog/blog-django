from django.contrib import admin

from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_at",
        "publish_date",
        "status",
        "is_published",
    )
    fields = (
        "author",
        "title",
        "slug",
        "summary",
        "content",
        "status",
        "created_at",
        "updated_at",
        "publish_date",
        "is_published",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "is_published",
    )
    list_filter = (
        "status",
        "created_at",
        "publish_date",
    )
    ordering = ("-created_at",)


admin.site.register(Post, PostAdmin)
