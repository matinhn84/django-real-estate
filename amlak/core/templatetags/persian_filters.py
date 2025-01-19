from django import template

register = template.Library()

def convert_to_persian_numbers(value):
    persian_numbers = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    value = str(value)
    for en, fa in persian_numbers.items():
        value = value.replace(en, fa)
    return value

register.filter('persian_numbers', convert_to_persian_numbers)
