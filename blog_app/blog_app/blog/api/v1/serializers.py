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
        fields = ("name", "body", "email", "publish_date")
        read_only_fields = ("publish_date",)
        extra_kwargs = {
            "email": {"write_only": True},
        }
