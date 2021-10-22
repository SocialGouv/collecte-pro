from django.db import models

from ordered_model.models import OrderedModel
from softdelete.models import SoftDeleteModel


class Parametre(OrderedModel, SoftDeleteModel):
    code = models.CharField("code", max_length=255)
    title = models.CharField("title", max_length=255, null=True)
    nom = models.CharField("nom", max_length=255, null=True)
    url = models.CharField("url", max_length=255, null=True)
    ordre = models.PositiveIntegerField("ordre", null=True)

    class Meta:
        ordering = ('order',)
        verbose_name = "Paramètre"
        verbose_name_plural = "Paramètres"
