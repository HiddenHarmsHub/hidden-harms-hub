from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def settings_value(name):
    """Get a value from django settings."""
    return getattr(settings, name, "")
