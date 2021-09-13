from django.db import models

from ckeditor.fields import RichTextField
from ordered_model.models import OrderedModel
from softdelete.models import SoftDeleteModel


class CGUItem(OrderedModel, SoftDeleteModel):
    title = models.CharField("title", max_length=255)
    slug = models.SlugField("slug", max_length=255)
    description = RichTextField("description", blank=True)

    class Meta:
        ordering = ('order',)
        verbose_name = "Item de C.G.U."
        verbose_name_plural = "Items de C.G.U."

    def __str__(self):
        return self.title
