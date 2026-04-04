from django import template

register = template.Library()

@register.filter
def dictkey(d, key):
    try:
        return d.get(key, None)
    except:
        return None


@register.filter
def in_list(value, arg):
    """
    Usage: {% if user.userprofile.role|in_list:"admin,doctor,nurse" %}
    """
    return value in arg.split(',')

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(int(key))  # Force key to int for dict with integer keys
    except (ValueError, TypeError, AttributeError):
        return None

@register.filter
def abs_val(value):
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value
    
@register.filter
def make_range(value):
    return range(value)