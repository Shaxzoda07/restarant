from django import template

register = template.Library()


@register.filter
def som(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (TypeError, ValueError):
        return value
