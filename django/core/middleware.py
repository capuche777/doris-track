"""Cross-cutting middleware for DorisTrack."""
from django.conf import settings
from django.contrib.auth.middleware import (
    LoginRequiredMiddleware as DjangoLoginRequiredMiddleware,
)


class LoginRequiredMiddleware(DjangoLoginRequiredMiddleware):
    """Require authentication site-wide, exempting static and media assets.

    Django's ``LoginRequiredMiddleware`` redirects every unauthenticated
    request (including ones for static and media files) to ``LOGIN_URL``. In
    development assets are served by Django rather than WhiteNoise, so without
    this exemption the login page itself would load without its CSS.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith((settings.STATIC_URL, settings.MEDIA_URL)):
            return None
        return super().process_view(request, view_func, view_args, view_kwargs)
