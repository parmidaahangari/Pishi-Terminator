# Put you code here
from django import template
register = template.Library()
@register.filter(name='topersian')
def topersian(value):
    eng_to_persian = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹",
    }
    result = ""
    for i in value:
        if i.isdigit() and i.isascii():
            result += eng_to_persian[i]
        else:
            result += i
    return result