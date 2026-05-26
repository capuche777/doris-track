"""Core app configuration."""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core app - shared utilities and main dashboard."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"