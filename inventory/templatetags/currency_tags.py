from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def indian_currency(value):
    """
    Formats a number or Decimal into Indian Currency notation.
    e.g., 154836.50 -> ₹1,54,836.50
    """
    if value is None or value == '':
        return "₹0.00"
    
    try:
        dec_val = Decimal(str(value))
    except Exception:
        return f"₹{value}"

    # Break into integer part and decimal part
    parts = f"{dec_val:.2f}".split('.')
    int_str = parts[0]
    dec_str = parts[1]

    is_negative = False
    if int_str.startswith('-'):
        is_negative = True
        int_str = int_str[1:]

    # Indian numbering formatting logic
    if len(int_str) <= 3:
        formatted_int = int_str
    else:
        last_three = int_str[-3:]
        other_digits = int_str[:-3]
        groups = []
        while len(other_digits) > 2:
            groups.insert(0, other_digits[-2:])
            other_digits = other_digits[:-2]
        if other_digits:
            groups.insert(0, other_digits)
        groups.append(last_three)
        formatted_int = ','.join(groups)

    prefix = "-₹" if is_negative else "₹"
    return f"{prefix}{formatted_int}.{dec_str}"
