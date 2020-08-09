from .common import *


INTERNAL_IPS = ["localhost", "0.0.0.0"]

# Testing
INSTALLED_APPS += ("django_nose",)
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
NOSE_ARGS = [
    BASE_DIR,
    "-s",
    "--nologcapture",
    "--with-coverage",
    "--with-progressive",
    "--cover-package=location",
]
