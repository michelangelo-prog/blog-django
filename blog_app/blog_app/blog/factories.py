from datetime import timedelta

from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from django.contrib.auth.models import User
from django.utils import timezone

from .models import Post, Comment


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = Sequence(lambda n: f"testuser{n}")
    password = Faker(
        "password",
        length=10,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )
    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    is_active = True
    is_staff = False


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    author = SubFactory(UserFactory)
    title = Sequence(lambda n: f"Title {n}")
    slug = Sequence(lambda n: f"title-{n}")
    summary = Sequence(lambda n: f"Summary-{n}")
    content = Faker("text")
    status = Post.STATUS.PUBLISH.value
    publish_date = timezone.now() - timedelta(days=1)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    post = SubFactory(PostFactory)
    name = Faker("name")
    email = Faker("email")
    body = Faker("text")
    published = False
    publish_date = timezone.now() - timedelta(days=1)
