from django.contrib import admin

from ordered_model.admin import OrderedModelAdmin

from soft_deletion.admin import SoftDeletedAdmin, IsActiveFilter

from .models import Parametre


@admin.register(Parametre)
class ParametreAdmin(SoftDeletedAdmin, OrderedModelAdmin):
    list_display = ('code', 'title', 'nom', 'url', 'ordre')
    list_filter = (IsActiveFilter,)
    search_fields = ('code', 'nom', 'title')
    ordering = ('code',)

