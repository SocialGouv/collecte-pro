import logging
import time
from datetime import date, timedelta

from django.conf import settings
from django.utils import timezone

from actstream import action
from ecc.celery import app
from celery.utils.log import get_task_logger

from control.models import Control, Questionnaire, ResponseFile
from parametres.models import Parametre
from utils.email import send_email


logger = get_task_logger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


ACTION_LOG_REPORT_VERB_SENT = 'files report email sent'
ACTION_LOG_REPORT_VERB_NOT_SENT = 'files report email not sent'
ACTION_LOG_DUE_VERB_SENT = 'due date report email sent'
ACTION_LOG_DUE_VERB_NOT_SENT = 'due date report email not sent'


def get_date_cutoff(control):
    """
    L'outil de reporting recherche les fichiers téléversés après une date spécifique :
    - La dernière fois qu'un email a été envoyé
    - ou bien depuis 24h
    """
    latest_email_sent = control.actor_actions.filter(verb=ACTION_LOG_REPORT_VERB_SENT).first()
    if latest_email_sent:
        date_cutoff = latest_email_sent.timestamp
    else:
        date_cutoff = timezone.now() - timedelta(hours=24)
    return date_cutoff


def get_files(control):
    date_cutoff = get_date_cutoff(control)
    logger.info("Recherche des fichiers téléversés après le {}".format(
        date_cutoff.strftime("%Y-%m-%d %H:%M:%S")))
    files = ResponseFile.objects.filter(
        question__theme__questionnaire__control=control,
        created__gt=date_cutoff,
    )
    logger.info(f'Fichiers trouvés : {len(files)}')
    return files


@app.task(queue=settings.CELERY_QUEUE)
def send_files_report():
    html_template = 'reporting/email/files_report.html'
    text_template = 'reporting/email/files_report.txt'
    for control in Control.objects.all():
        logger.info(f'Contrôle : {control.id}')
        if control.depositing_organization:
            subject = control.depositing_organization
        else:
            subject = control.title
        subject += ' - de nouveaux documents déposés !'
        files = get_files(control)
        if not files:
            logger.info(f'Pas de nouveau document, arrêt.')
            continue
        recipient_list = [
            access.userprofile.user.email
            for access in control.access.all()
            if access.userprofile.send_files_report==True
        ]
        if not recipient_list:
            logger.info(f'Pas de destinataire, arrêt.')
            continue
        logger.debug(f'Destinataires : {len(recipient_list)}')
        date_cutoff = get_date_cutoff(control)
        context = {
            'control': control,
            'date_cutoff': date_cutoff.strftime("%A %d %B %Y"),
            'files': files,
        }
        number_of_sent_email = send_email(
            to=recipient_list,
            subject=subject,
            html_template=html_template,
            text_template=text_template,
            extra_context=context,
        )
        logger.info(f"{number_of_sent_email} emails envoyés.")
        number_of_recipients = len(recipient_list)
        if number_of_sent_email != number_of_recipients:
            logger.warning(
                f'Il y avait {number_of_recipients} destinataires(s), '
                f'et {number_of_sent_email} email(s) envoyé(s).')
        if number_of_sent_email > 0:
            logger.info(f'Email envoyé pour le contrôle {control.id}')
            action.send(sender=control, verb=ACTION_LOG_REPORT_VERB_SENT)
        else:
            logger.info(f'Aucun email envoyé pour le contrôle {control.id}')
            action.send(sender=control, verb=ACTION_LOG_REPORT_VERB_NOT_SENT)

        EMAIL_SPACING_TIME_SECONDS = settings.EMAIL_SPACING_TIME_MILLIS / 1000
        logger.info(
            f'Attente de {EMAIL_SPACING_TIME_SECONDS}s après reporting pour le contrôle {control.id}')
        time.sleep(EMAIL_SPACING_TIME_SECONDS)


@app.task(queue=settings.CELERY_QUEUE)
def send_notifs_dates_echeances():
    html_template = "reporting/email/notif_date_echeance.html"
    text_template = "reporting/email/notif_date_echeance.txt"
    jours_echeance = Parametre.objects.filter(code="JOURS_ECHEANCE").filter(deleted_at__isnull=True).first()
    try:
        jours_echeance = int(jours_echeance.name)
    except:
        jours_echeance = settings.JOURS_ECHEANCE
    logger.info(f"Jours : {jours_echeance}")
    for questionnaire in Questionnaire.objects.filter(end_date__isnull=False).all():
        date_relance = questionnaire.end_date - timedelta(days=jours_echeance)
        if date_relance == date.today():
            logger.info(f"Questionnaire : {questionnaire.id}")
            if questionnaire.control.depositing_organization:
                subject = questionnaire.control.depositing_organization
            else:
                subject = questionnaire.control.title
            subject += f" - Questionnaire : {questionnaire.title}"
            subject += " - la date de réponse arrive bientôt à échéance."
            recipient_list = [
                access.userprofile.user.email
                for access in questionnaire.control.access.all()
            ]
            if not recipient_list:
                logger.info(f"Pas de destinataire, arrêt.")
                continue
            logger.debug(f"Destinataires : {len(recipient_list)}")
            context = {
                "questionnaire": questionnaire,
                "jours_echeance": jours_echeance,
            }
            number_of_sent_email = send_email(
                to=recipient_list,
                subject=subject,
                html_template=html_template,
                text_template=text_template,
                extra_context=context,
            )
            logger.info(f"{number_of_sent_email} emails envoyés.")
            number_of_recipients = len(recipient_list)
            if number_of_sent_email != number_of_recipients:
                logger.warning(
                    f"Il y avait {number_of_recipients} destinataires(s), "
                    f"et {number_of_sent_email} email(s) envoyé(s)."
                )
            if number_of_sent_email > 0:
                logger.info(f"Email envoyé pour le questionnaire {questionnaire.id}")
                action.send(sender=questionnaire, verb=ACTION_LOG_DUE_VERB_SENT)
            else:
                logger.info(f"Aucun email envoyé pour le questionnaire {questionnaire.id}")
                action.send(sender=questionnaire, verb=ACTION_LOG_DUE_VERB_NOT_SENT)
