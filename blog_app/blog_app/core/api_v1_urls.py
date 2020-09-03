from blog_app.blog.api.v1 import (comments_list_view, post_lists_view,
                                  post_retrieve_view)
from django.urls import path

urlpatterns = [
    path("posts/", post_lists_view, name="posts"),
    path("posts/<slug:slug>/", post_retrieve_view, name="post"),
    path("posts/<slug:slug>/comments", comments_list_view, name="post_comments",),
]
