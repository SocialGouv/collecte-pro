import os

from django.dispatch import receiver
from django.conf import settings

from .api_views import questionnaire_api_post_save, questionnaire_api_post_update
from .models import Questionnaire
from .upload_path import questionnaire_path
from parametres.models import Parametre
from utils.email import send_email


@receiver(questionnaire_api_post_save, sender=Questionnaire)
def create_questionnaire_path(instance, **kwargs):
    """
    Create the questionnaire folder after the API's save.
    """
    questionnaire = instance
    relative_path = questionnaire_path(questionnaire)
    absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    if not os.path.exists(absolute_path):
        os.makedirs(absolute_path)


@receiver(questionnaire_api_post_update, sender=Questionnaire)
def send_email_when_answered(instance, session_user, **kwargs):
    """
    Envoi d'un email lorsque le questionnaire est marqué "Répondu" par un répondant.
    """
    if instance.is_replied:
        # On envoie le mail à tous les membres de l'espace de dépôt
        access = instance.control.access
        recipients = [session_user.email, ]
        users = access.values_list('userprofile__user', flat=True)
        users = users.exclude(id=session_user.id)
        emails = users.values_list('userprofile__user__email', flat=True)
        support_email = Parametre.objects.filter(code="SUPPORT_EMAIL").filter(deleted_at__isnull=True).first()
        if isinstance(support_email, dict):
            support_email = support_email["url"]
        else:
            support_email = support_email.url
        context = {
            'questionnaire': instance,
            'user': session_user,
            'support_team_email': support_email,
        }
        send_email(
            to=recipients,
            cc=emails,
            subject=f'collecte-pro - Questionnaire marqué comme répondu - {instance}',
            html_template='control/email_is_replied.html',
            text_template='control/email_is_replied.txt',
            extra_context=context,
        )
