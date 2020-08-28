from rest_framework import serializers

from ...models import Comment, Post


class ListPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "slug", "summary", "publish_date")
        lookup_field = "slug"


class RetrievePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "summary", "content", "publish_date")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("name", "body", "email", "created_at")
        read_only_fields = ("created_at",)
        extra_kwargs = {
            "email": {"write_only": True},
        }
