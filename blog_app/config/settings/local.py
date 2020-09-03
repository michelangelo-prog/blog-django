import sys

from .common import *

INTERNAL_IPS = ["localhost", "0.0.0.0", "127.0.0.1"]

# Django Debug Toolbar
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

if not TESTING and DEBUG:
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
    if "django.contrib.staticfiles" not in INSTALLED_APPS:
        INSTALLED_APPS += ["django.contrib.staticfiles"]
    INSTALLED_APPS += ["debug_toolbar"]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

# Testing
INSTALLED_APPS += ("django_nose",)
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
NOSE_ARGS = [
    BASE_DIR,
    "-s",
    "--nologcapture",
    "--with-coverage",
    "--with-progressive",
    "--cover-package=blog_app",
]

# CORS
CORS_ORIGIN_WHITELIST = ["http://localhost:3000"]
