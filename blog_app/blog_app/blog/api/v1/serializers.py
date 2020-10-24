from rest_framework import serializers

from ...models import Comment, Post, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("title", "slug")


class ListPostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = ("title", "slug", "summary", "publish_date", "tags")
        lookup_field = "slug"


class RetrievePostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = ("title", "summary", "content", "publish_date", "tags")

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("name", "body", "email", "publish_date")
        read_only_fields = ("publish_date",)
        extra_kwargs = {
            "email": {"write_only": True},
        }
