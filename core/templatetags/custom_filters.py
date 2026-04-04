from django import template
register = template.Library()

@register.filter
def until(value):
    return range(value)