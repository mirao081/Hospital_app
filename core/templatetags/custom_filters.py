from django import template
register = template.Library()

@register.filter
def until(value):
    return range(value)

@register.filter
def make_range(value):
    """Returns a range from 0 to value-1"""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return []