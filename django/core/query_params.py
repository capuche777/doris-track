"""Helpers for parsing API query parameters."""
from datetime import date

from rest_framework.exceptions import ValidationError


def parse_positive_int(request, param, default):
    """Parse a positive integer query param, falling back to ``default``."""
    raw = request.query_params.get(param)
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def parse_iso_date(request, param):
    """Parse an ISO date query param, or None. Raises 400 on a malformed value."""
    raw = request.query_params.get(param)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise ValidationError({param: "Must be an ISO date (YYYY-MM-DD)."})
