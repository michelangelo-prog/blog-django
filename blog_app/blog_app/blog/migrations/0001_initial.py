# Generated by Django 3.0.8 on 2020-08-11 10:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=75, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("summary", models.CharField(max_length=255)),
                ("content", models.TextField()),
                (
                    "status",
                    models.IntegerField(
                        choices=[(0, "draft"), (1, "publish")], default=0
                    ),
                ),
                ("publish_date", models.DateTimeField(blank=True, null=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="blog_posts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
    ]
