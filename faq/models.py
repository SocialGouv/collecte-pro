from django.db import models

from django_ckeditor_5.fields import CKEditor5Field
from ordered_model.models import OrderedModel
from django_softdelete.models import SoftDeleteModel


class FAQItem(OrderedModel, SoftDeleteModel):
    title = models.CharField("title", max_length=255)
    slug = models.SlugField("slug", max_length=255)
    description = CKEditor5Field("description", blank=True, config_name='default')

    class Meta:
        ordering = ('order',)
        verbose_name = "Item de F.A.Q"
        verbose_name_plural = "Items de F.A.Q"

    def __str__(self):
        return self.title
