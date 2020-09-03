from blog_app.blog.api.v1 import views as blog_views
from django.urls import path

urlpatterns = [
    path("posts/", blog_views.PostsList.as_view(), name="posts"),
    path("posts/<slug:slug>/", blog_views.PostRetrieve.as_view(), name="post"),
    path(
        "posts/<slug:slug>/comments",
        blog_views.CommentsList.as_view(),
        name="post_comments",
    ),
]
