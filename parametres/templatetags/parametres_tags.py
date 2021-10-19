from django import template

from parametres.models import Parametre

register = template.Library()

@register.simple_tag
def get_parametre_items():
    return Parametre.objects.filter(code="LIEN_FOOTER").order_by('ordre')