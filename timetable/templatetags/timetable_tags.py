from django import template

register = template.Library()

@register.filter
def dicthash(d, key):
    if isinstance(d, dict):
        return d.get(key)
    return None
