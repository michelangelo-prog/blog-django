from django.contrib import admin

from .models import Comment, Post


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


class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "body", "post", "created_at", "publish_date", "published", "is_published")
    readonly_fields = (
        "created_at",
        "is_published",
    )
    list_filter = ("published", "created_at", "publish_date")
    actions = ["make_published", "make_unpublished"]

    def make_published(self, request, queryset):
        queryset.update(published=True)

    def make_unpublished(self, request, queryset):
        queryset.update(published=False)


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
