"""Custom template filters for scores app."""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get a value from a dict by key. Returns empty string if key not found."""
    if dictionary is None:
        return ""
    return dictionary.get(str(key), dictionary.get(key, ""))
