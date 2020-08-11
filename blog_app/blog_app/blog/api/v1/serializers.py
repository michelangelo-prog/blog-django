from rest_framework import serializers

from ...models import Post


class ListPostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ("url", "title", "summary", "publish_date")
        lookup_field = "slug"
        extra_kwargs = {"url": {"lookup_field": "slug"}}


class RetrievePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "summary", "content", "publish_date")
