"""Development settings for DorisTrack."""
import socket

from .base import *

DEBUG = True
SECRET_KEY = "dev-secret-key-for-local-testing-only"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]

# Debug Toolbar must run as early as possible in the middleware chain.
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware", *MIDDLEWARE]

# Inside Docker the request arrives from the container gateway, not 127.0.0.1.
# Derive the gateway (x.x.x.1) from the container's own IPs so the toolbar's
# default INTERNAL_IPS check passes. 10.0.2.2 covers Docker Desktop on macOS.
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]