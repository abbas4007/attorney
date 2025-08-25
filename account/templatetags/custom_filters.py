# templatetags/custom_filters.py
import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def clean_html(value) :
    if not value :
        return value

    # حذف تمام انواع &nbsp; (با هر حالتی از حروف)
    cleaned = re.sub(r'&nbsp;|&\#160;|&\#xa0;', ' ', value, flags = re.IGNORECASE)

    # حذف spaceهای اضافی ایجاد شده
    cleaned = re.sub(r'\s+', ' ', cleaned)

    return mark_safe(cleaned)