from rest_framework import serializers

from ...models import Post


class ListPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "slug", "summary", "publish_date")
        lookup_field = "slug"


class RetrievePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "summary", "content", "publish_date")
