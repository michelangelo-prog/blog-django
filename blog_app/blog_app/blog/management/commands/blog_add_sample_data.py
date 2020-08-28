import argparse
from datetime import timedelta

from blog_app.blog.factories import PostFactory
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils import timezone


class Command(BaseCommand):
    help = "Add sample posts to user."

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument(
            "quantity", type=self._check_positive, help="number of posts"
        )

    def _check_positive(self, value):
        int_value = int(value)
        if int_value > 0:
            return int_value
        else:
            raise argparse.ArgumentTypeexitError(
                "%s is an invalid positive int value" % value
            )

    def handle(self, *args, **options):
        username, quantity = options["username"], options["quantity"]
        try:
            user = User.objects.get(username=username)
            for i in range(quantity):
                publish_date = timezone.now() - timedelta(days=i)
                PostFactory.create(author=user, publish_date=publish_date)
        except User.DoesNotExist:
            raise CommandError("User with username '%s' does not exist" % username)
        except IntegrityError as e:
            raise CommandError("Articles already exists: %s" % e)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully created %s articles for '%s' " % (quantity, username)
            )
        )
