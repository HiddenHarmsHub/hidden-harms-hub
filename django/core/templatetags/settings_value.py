from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def settings_value(name):
    """Get a value from django settings.

    Args:
        name (str): The key for the value required.

    Returns:
        str: The value of the setting with the key matching `name` or an empty string.
    """
    return getattr(settings, name, "")
