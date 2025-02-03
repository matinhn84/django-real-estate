from django.contrib.humanize.templatetags.humanize import intcomma

# Persian digits mapping
EN_TO_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def format_persian_price(number):
    """Formats number with commas and converts digits to Persian."""
    formatted_number = intcomma(number)  # Add commas: 1200000 -> "1,200,000"
    return formatted_number.translate(EN_TO_FA_DIGITS)  # Convert to Persian
