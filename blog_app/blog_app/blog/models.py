from django.contrib.auth.models import User
from django.db import models

from .behaviors import Timestampable


class Post(Timestampable, models.Model):
    class STATUS(models.IntegerChoices):
        DRAFT = (0, "draft")
        PUBLISH = (1, "publish")

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=300, unique=True)
    content = models.TextField()
    status = models.IntegerField(choices=STATUS.choices, default=STATUS.DRAFT)
    publish_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
