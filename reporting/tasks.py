import logging
import os
import shutil
from django.db import connection
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

        
@app.task(queue=settings.CELERY_QUEUE)
def identify_purgeable_controls(*args, **kwargs):
    INTERVAL_PURGE = 'interval_purge'
    ENVOI_NOTIF_MAIL = 'envoi_notif_mail'

    # Dictionnaire de traduction FR -> EN pour les intervalles
    INTERVAL_MAP = {
        **{f"{i} mois": f"{i} month" if i == 1 else f"{i} months" for i in range(1, 13)},
        **{f"{i} an" + ("s" if i > 1 else ""): f"{i} year" + ("s" if i > 1 else "") for i in range(1, 6)}
    }

    VAL_ENVOI_NOTIF_MAIL_FR = {'Oui': True, 'Non': False}
    
    interval_purge_fr = kwargs.get(INTERVAL_PURGE)
    if isinstance(interval_purge_fr, str):
        interval_purge_fr = interval_purge_fr.strip()

    envoi_notif_mail_fr = kwargs.get(ENVOI_NOTIF_MAIL)
    if isinstance(envoi_notif_mail_fr, str):
        envoi_notif_mail_fr = envoi_notif_mail_fr.strip()


    
    interval_purge = INTERVAL_MAP.get(interval_purge_fr)
    if interval_purge is None:
        logger.error(
            f"Le paramètre 'interval_purge' est manquant ou invalide (valeur reçue : '{interval_purge_fr}'). "
            f"Aucune procédure ne sera appelée."
        )
        return  

    
    envoi_notif_mail = VAL_ENVOI_NOTIF_MAIL_FR.get(envoi_notif_mail_fr, False)
    if envoi_notif_mail_fr not in VAL_ENVOI_NOTIF_MAIL_FR:
        logger.error(
            f"Le paramètre 'envoi_notif_mail' est manquant ou invalide (valeur reçue : '{envoi_notif_mail_fr}'). "
            f"Valeur par défaut utilisée : 'Non'."
        )

    logger.info(f"interval_purge (EN) = {interval_purge}")
    logger.info(f"envoi_notif_mail = {envoi_notif_mail}")

    try:
        with connection.cursor() as cursor:
            cursor.callproc('identify_purgeable_controls', [interval_purge])
            results = cursor.fetchall()

            if not results:
                logger.info("Aucun espace de dépôt éligible à la suppression.")
                return

            if envoi_notif_mail:
                for mail_inspecteur, espaces_depot, _ in results:
                    logger.info(f"Envoi mail à : {mail_inspecteur} pour espaces : {espaces_depot}")
                    send_mail_identify_purgeable_controls(mail_inspecteur, espaces_depot)

            return results

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la procédure stockée : {e}")


        
@app.task(queue=settings.CELERY_QUEUE)
def logical_delete_controls():
    try:
        with connection.cursor() as cursor:
            cursor.callproc('logical_delete_controls')
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la procédure stockée : {e}")


@app.task(queue=settings.CELERY_QUEUE)
def physical_delete_controls(*args, **kwargs):
    
    INTERVAL_PURGE_REP_ORPH= 'interval_purge_rep_orph'
    # Dictionnaire de traduction FR -> EN pour les intervalles
    INTERVAL_MAP = {
        **{f"{i} mois": f"{i} month" if i == 1 else f"{i} months" for i in range(1, 13)},
        **{f"{i} an" + ("s" if i > 1 else ""): f"{i} year" + ("s" if i > 1 else "") for i in range(1, 6)}
    }
    
    interval_purge_rep_orph_fr = kwargs.get(INTERVAL_PURGE_REP_ORPH)
    if isinstance(interval_purge_rep_orph_fr, str):
        interval_purge_rep_orph_fr = interval_purge_rep_orph_fr.strip()
    
    interval_purge_rep_orph = INTERVAL_MAP.get(interval_purge_rep_orph_fr)
    if interval_purge_rep_orph is None:
        logger.error(
            f"Le paramètre 'interval_purge_rep_orph' est manquant ou invalide (valeur reçue : '{interval_purge_rep_orph_fr}'). "
            f"Aucune procédure ne sera appelée."
        )
        return  

    logger.info(f"interval_purge_rep_orph (EN) = {interval_purge_rep_orph}")

    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pec.reference_code
                FROM purge_eligible_control_trv pec 
                INNER JOIN control_control cc ON pec.control_id = cc.id
                WHERE cc.is_model = FALSE
            """)
            results = cursor.fetchall()

            for row in results:
                reference_code = row[0]
                delete_media_directory(reference_code)

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la requête -  delete_media_directory : {e}")
    
    try:
        with connection.cursor() as cursor:
            cursor.callproc('physical_delete_controls', [interval_purge_rep_orph])
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la procédure stockée : {e}")

def delete_media_directory(reference_code):
    media_root = settings.MEDIA_ROOT

    target_path = os.path.abspath(os.path.join(media_root, reference_code))

    if not target_path.startswith(os.path.abspath(media_root)):
        logger.error(f"Refusé : le chemin cible sort de MEDIA_ROOT. ({target_path})")
        return 

    if os.path.exists(target_path) and os.path.isdir(target_path):
        try:
            shutil.rmtree(target_path)
            logger.info(f"Supprimé : {target_path}")
        except Exception as e:
            logger.error(f"Erreur pendant la suppression : {e}")
    else:
        logger.info(f"Le dossier n'existe pas : {target_path}")



def send_mail_identify_purgeable_controls(mail_inspecteur, espaces_depot):
    html_template = "reporting/email/notif_espace_depot_elig_supp.html"
    text_template = "reporting/email/notif_espace_depot_elig_supp.txt"
    
    subject = "Notification : Espaces de dépôt éligibles à la suppression"
    recipient_list = [mail_inspecteur]
    
    logger.info("Destinataire: %s", recipient_list)
    
    espaces_depot_list = espaces_depot.split(";") if espaces_depot else []

    context = {
        "list_espace_depot": espaces_depot_list, 
    }

    send_email(
        to=recipient_list,
        subject=subject,
        html_template=html_template,
        text_template=text_template,
        extra_context=context,
    )
    
    logger.info(f"Email envoyé à {mail_inspecteur} pour les espaces : {espaces_depot}")



            