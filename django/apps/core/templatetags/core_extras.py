"""Custom template filters for core app."""
from django import template

register = template.Library()

@register.filter
def lookup(dict, key):
    """Access dict by key, returns empty string if not found."""
    return dict.get(key, "")
