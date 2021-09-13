from django import template

from tos.models import CGUItem

register = template.Library()

@register.simple_tag
def get_cgu_items():
    return CGUItem.objects.filter(deleted_at__isnull=True)
