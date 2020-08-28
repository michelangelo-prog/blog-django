from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ...models import Post
from .serializers import (CommentSerializer, ListPostSerializer,
                          RetrievePostSerializer)


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
        ViewSet for viewing posts.
    """

    lookup_field = "slug"
    queryset = Post.objects.get_published_posts()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "list":
            return ListPostSerializer
        if self.action == "retrieve":
            return RetrievePostSerializer
        if self.action == "comments":
            return CommentSerializer

    @action(methods=["get", "post"], detail=True, permission_classes=(AllowAny,))
    def comments(self, request, slug=None):
        post = self.get_object()
        if request.method == "GET":
            comments = post.get_published_comments()
            serializer = self.get_serializer(comments, many=True)
            return Response(serializer.data)
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data["post"] = post
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
