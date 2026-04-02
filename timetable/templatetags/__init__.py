from django import template

register = template.Library()

@register.filter
def dicthash(d, key):
    """Template filter: {{ mydict|dicthash:key }}"""
    if isinstance(d, dict):
        return d.get(key)
    return None
