from django.contrib import admin

from .models import Alert

from logs.actions import add_log_entry


def alert_delete(modeladmin, request, queryset):
    for item in queryset:
        item.delete()
        add_log_entry(verb='alert deleted', session_user=request.user, obj=item, target=None)

alert_delete.short_description = "Supprimer les alertes sélectionnées"


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("text", "start_date", "end_date")
    search_fields = ("text",)
    ordering = ("-end_date", "start_date",)
    actions = [alert_delete]

    def has_delete_permission(self, request, obj=None):
        return False
