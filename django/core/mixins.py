"""Reusable model mixins for DorisTrack."""

from django.db import models


class TimestampedModel(models.Model):
    """Mixin that adds created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
