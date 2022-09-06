from django.db import models


class Alert(models.Model):
    text = models.CharField(
        "texte",
        help_text="Message affiché sur la page de connexion",
        max_length=255,
    )
    start_date = models.DateTimeField(
        verbose_name="heure d'affichage", blank=True, null=True,
        help_text="Heure d'affichage de l'alerte")
    end_date = models.DateTimeField(
        verbose_name="heure d'échéance", blank=True, null=True,
        help_text="Heure de fin d'affichage de l'alerte")

    class Meta:
        ordering = ("start_date",)
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
