from django.db import models

from ckeditor.fields import RichTextField
from ordered_model.models import OrderedModel
from softdelete.models import SoftDeleteModel


class Parametre(OrderedModel, SoftDeleteModel):
    code = models.CharField("code", max_length=255)
    nom = models.CharField("nom", max_length=255)
    url = models.CharField("url", max_length=255)
    ordre = models.PositiveIntegerField("ordre")

    class Meta:
        ordering = ('order',)
        verbose_name = "Paramètre"
        verbose_name_plural = "Paramètres"
