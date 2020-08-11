from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ...models import Post
from .serializers import ListPostSerializer, RetrievePostSerializer


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
