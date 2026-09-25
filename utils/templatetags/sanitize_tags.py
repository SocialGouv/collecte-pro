from django import template
from django.utils.safestring import mark_safe

from utils.sanitize import sanitize_rich_text

register = template.Library()


@register.filter(name="sanitize_html")
def sanitize_html(value):
    """Sanitize a CKEditor5 rich-text value for safe rendering (replaces `|safe`)."""
    return mark_safe(sanitize_rich_text(value))
