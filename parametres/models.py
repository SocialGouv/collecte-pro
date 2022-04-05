from django.db import models

from ordered_model.models import OrderedModel
from django_softdelete.models import SoftDeleteModel


class Parametre(OrderedModel, SoftDeleteModel):
    code = models.CharField(
        "code",
        help_text="LIEN_FOOTER, LOGO_FOOTER, ENTITY_PICTURE, SUPPORT_EMAIL",
        max_length=255,
    )
    title = models.CharField(
        "title",
        help_text="attribut 'title' des paramètres de type 'lien'",
        max_length=255,
        null=True,
    )
    name = models.CharField(
        "name",
        help_text="Texte affiché pour les paramètres de type 'lien' et texte alternatif pour les paramètres de type 'image'",
        max_length=255,
        null=True,
    )
    url = models.CharField(
        "url",
        help_text="url de destination pour les paramètres de type 'lien' et url de l'image pour les paramètres de type 'image'",
        max_length=255,
        null=True,
    )

    class Meta:
        ordering = ('order',)
        verbose_name = "Paramètre"
        verbose_name_plural = "Paramètres"
