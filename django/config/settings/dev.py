"""Development settings for DorisTrack."""
from .base import *

DEBUG = True
SECRET_KEY = "dev-secret-key-for-local-testing-only"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]