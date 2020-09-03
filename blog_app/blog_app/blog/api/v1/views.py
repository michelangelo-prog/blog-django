from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import Http404

from ...models import Post
from .serializers import (CommentSerializer, ListPostSerializer,
                          RetrievePostSerializer)


class PostsList(APIView):
    """
    View to list posts.
    """

    permission_classes = (AllowAny,)

    def get(self, request):
        posts = Post.objects.get_published_posts()
        paginator = LimitOffsetPagination()
        try:
            result_page = paginator.paginate_queryset(posts, request)
            serializer = ListPostSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except AttributeError:
            serializer = ListPostSerializer(posts, many=True)
            return Response(serializer.data, status.HTTP_200_OK)


class PostMixin:
    def get_object(self, slug):
        try:
            return Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise Http404

    class Meta:
        abstract = True


class PostRetrieve(PostMixin, APIView):

    permission_classes = (AllowAny,)

    def get(self, request, slug=None):
        post = self.get_object(slug)
        serializer = RetrievePostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentsList(PostMixin, APIView):

    permission_classes = (AllowAny,)

    def get(self, request, slug=None):
        post = self.get_object(slug)
        comments = post.get_published_comments()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, slug=None):
        post = self.get_object(slug)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["post"] = post
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
