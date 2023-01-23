from django import template

from parametres.models import Parametre

register = template.Library()

@register.simple_tag
def get_liens_footer_items():
    return Parametre.objects.filter(code="LIEN_FOOTER").filter(deleted_at__isnull=True).order_by("order")

@register.simple_tag
def get_logo_footer_item():
    return Parametre.objects.filter(code="LOGO_FOOTER").filter(deleted_at__isnull=True).first() or {
        "url": "img/logo-footer.png",
        "title": "République française. Liberté, égalité, fraternité",
    }

@register.simple_tag
def get_entity_picture_item():
    return Parametre.objects.filter(code="ENTITY_PICTURE").filter(deleted_at__isnull=True).first() or {
        "url": "img/picture-Republique-francaise.png",
        "title": "République française. Liberté, égalité, fraternité",
    }

@register.simple_tag
def get_support_email_item():
    return Parametre.objects.filter(code="SUPPORT_EMAIL").filter(deleted_at__isnull=True).first() or {
        "url": "support@collecte-pro.gouv.fr",
        "title": "Mail de support",
    }
