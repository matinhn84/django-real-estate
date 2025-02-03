from django import template
from properties.utils import format_persian_price  # Import your function

register = template.Library()

@register.filter
def persian_price(value):
    return format_persian_price(value)
