import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .behaviors import Creatable, Updatable


class PostManager(models.Manager):
    def get_published_posts(self):
        return self.filter(
            status=Post.STATUS.PUBLISH, publish_date__lte=timezone.now()
        ).order_by("-publish_date")


class Post(Creatable, Updatable, models.Model):
    class STATUS(models.IntegerChoices):
        DRAFT = (0, "draft")
        PUBLISH = (1, "publish")

    objects = PostManager()

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    title = models.CharField(max_length=75, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    summary = models.CharField(max_length=255)
    content = models.TextField()
    status = models.IntegerField(choices=STATUS.choices, default=STATUS.DRAFT)
    publish_date = models.DateTimeField(null=True, blank=True)

    @property
    def is_published(self):
        return (
            self.status == self.STATUS.PUBLISH and self.publish_date <= timezone.now()
        )

    def get_published_comments(self):
        return self.comments.filter(
            published=True, publish_date__lte=timezone.now()
        ).order_by("-publish_date")

    def __str__(self):
        return self.title


class Comment(Creatable, models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(default=datetime.datetime.now())

    @property
    def is_published(self):
        return self.published and self.publish_date <= timezone.now()

    class Meta:
        ordering = ["-publish_date"]

    def __str__(self):
        return "Comment {} by {}".format(self.body, self.name)
