from django.conf import settings
from django.db import models
from django.apps import apps
from django.db.models import Q

from annoying.fields import AutoOneToOneField

from .managers import UserProfileQuerySet

class UserIpAddress(models.Model):
    ip = models.CharField(max_length=30)
    username = models.EmailField(max_length=254)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Adresse IP Utilisateur"
        verbose_name_plural = "Adresses IP Utilisateurs"

class UserProfile(models.Model):
    AUDITED = 'audited'
    INSPECTOR = 'inspector'
    PROFILE_TYPE = (
        (AUDITED, 'Organisme interrogé'),
        (INSPECTOR, 'Demandeur'),
    )
    user = AutoOneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE,
        related_name='profile')
    profile_type = models.CharField(max_length=255, choices=PROFILE_TYPE)
    organization = models.CharField("Organisme", max_length=255, blank=True, null=True)
    send_files_report = models.BooleanField(
        verbose_name="Envoi Rapport de Fichiers", default=True,
        help_text="Envoyer par email le rapport des fichiers déposés ?")
    agreed_to_tos = models.BooleanField(
        default=False, verbose_name="accepté CGU",
        help_text="Les Conditions Générales d'Utilisation ont-elles été acceptées ?")

    objects = UserProfileQuerySet.as_manager()

    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"

    @property
    def is_inspector(self):
        return self.profile_type == self.INSPECTOR

    @property
    def is_audited(self):
        return self.profile_type == self.AUDITED

    @property
    def questionnaires(self):
        """
        Returns the questionnaires belonging to the user.
        """
        Questionnaire = apps.get_model('control.Questionnaire')
        inspected_controls = self.user_controls('demandeur')
        audited_controls = self.user_controls('repondant')
        inspected_questionnaires = Questionnaire.objects.filter(control__in=inspected_controls)
        audited_questionnaires = Questionnaire.objects.filter(Q(control__in=audited_controls) & Q(is_draft=False))
        return inspected_questionnaires | audited_questionnaires

    def user_controls(self, accesstype):
        """
        Returns the controls by access belonging to the user.
        """
        Control = apps.get_model('control.Control')
        if accesstype == 'all':
            all_user_controls = Control.objects.filter(access__in=self.access.all())
            return all_user_controls
        filtered_user_controls = Control.objects.filter(access__in=self.access.filter(access_type=accesstype).all())
        return filtered_user_controls.distinct()

    def __str__(self):
        return str(self.user)

class Access(models.Model):
    REPONDANT = 'repondant'
    DEMANDEUR = 'demandeur'
    ACCESS_TYPE = (
        (REPONDANT, 'Répondant'),
        (DEMANDEUR, 'Demandeur'),
    )
    access_type = models.CharField(max_length=255, choices=ACCESS_TYPE)
    userprofile = models.ForeignKey(
        to='Userprofile', verbose_name='userprofile', related_name='access',
        blank=True, on_delete=models.CASCADE)
    control = models.ForeignKey(
        to='control.Control', related_name='access', on_delete=models.PROTECT,
        blank=True)

    class Meta:
        verbose_name = "Accès d'un utilisateur à un contrôle"
        verbose_name_plural = "Accès des utilisateurs à des contrôles"
