from django.contrib import admin

from ordered_model.admin import OrderedModelAdmin

from soft_deletion.admin import SoftDeletedAdmin, IsActiveFilter

from .models import Parametre


@admin.register(Parametre)
class ParametreAdmin(SoftDeletedAdmin, OrderedModelAdmin):
    list_display = ('code', 'title', 'name', 'url', 'order', 'move_up_down_links')
    readonly_fields = ('order',)
    list_filter = (IsActiveFilter,)
    search_fields = ('code', 'name', 'title')
    ordering = ('order',)
