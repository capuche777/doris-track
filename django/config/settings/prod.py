"""Production settings for DorisTrack."""
from .base import *
import os

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# Gunicorn does not use ASGI_APPLICATION, it uses WSGI_APPLICATION
# Keep WSGI for gunicorn compatibility
# ASGI_APPLICATION = "config.asgi.application"