from django import template
from django.utils import timezone
import jdatetime

register = template.Library()

@register.filter
def to_jalali(value, format='%Y/%m/%d'):
    if not value:
        return ''
    gdate = timezone.localtime(value)
    jdate = jdatetime.date.fromgregorian(date=gdate)
    return jdate.strftime(format)