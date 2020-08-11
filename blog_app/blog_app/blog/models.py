from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .behaviors import Timestampable


class PostManager(models.Manager):
    def get_published_post(self, slug):
        return (
            self.filter(
                status=Post.STATUS.PUBLISH, publish_date__lte=timezone.now(), slug=slug
            )
            .order_by()
            .first()
        )

    def get_published_posts(self):
        return self.filter(
            status=Post.STATUS.PUBLISH, publish_date__lte=timezone.now()
        ).order_by("-publish_date")


class Post(Timestampable, models.Model):
    objects = PostManager()

    class STATUS(models.IntegerChoices):
        DRAFT = (0, "draft")
        PUBLISH = (1, "publish")

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    title = models.CharField(max_length=75, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    summary = models.CharField(max_length=255)
    content = models.TextField()
    status = models.IntegerField(choices=STATUS.choices, default=STATUS.DRAFT)
    publish_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
