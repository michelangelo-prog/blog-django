from django.contrib import admin

from .models import Post


class PostAdmin(admin.ModelAdmin):
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
    )
    readonly_fields = ("created_at", "updated_at")

    ordering = ("-created_at",)


admin.site.register(Post, PostAdmin)
