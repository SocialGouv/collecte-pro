import csv
import glob
import logging
import os
import shutil
import zipfile
from collections import defaultdict
from io import BytesIO, StringIO
from statistics import mean
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
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


ACTION_LOG_REPORT_VERB_SENT = "files report email sent"
ACTION_LOG_REPORT_VERB_NOT_SENT = "files report email not sent"
ACTION_LOG_DUE_VERB_SENT = "due date report email sent"
ACTION_LOG_DUE_VERB_NOT_SENT = "due date report email not sent"

DISK_USAGE_REPORT_DIRNAME = "rapports_poids_fichiers"
DISK_USAGE_REPORT_FILENAME_PREFIX = "collecte-pro_poids_fichiers_"


def human_readable_size(size_bytes):
    """
    Convertit une taille en octets vers une chaîne lisible, avec l'unité
    la plus adaptée (octets, Ko, Mo, Go, To).
    """
    size = float(size_bytes)
    for unit in ("octets", "Ko", "Mo", "Go", "To"):
        if size < 1024 or unit == "To":
            if unit == "octets":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024


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
    logger.info("Recherche des fichiers téléversés après le {}".format(date_cutoff.strftime("%Y-%m-%d %H:%M:%S")))
    files = ResponseFile.objects.filter(
        question__theme__questionnaire__control=control,
        created__gt=date_cutoff,
    )
    logger.info(f"Fichiers trouvés : {len(files)}")
    return files


@app.task(queue=settings.CELERY_QUEUE)
def send_files_report():
    html_template = "reporting/email/files_report.html"
    text_template = "reporting/email/files_report.txt"
    for control in Control.objects.all():
        logger.info(f"Contrôle : {control.id}")
        if control.depositing_organization:
            subject = control.depositing_organization
        else:
            subject = control.title
        subject += " - de nouveaux documents déposés !"
        files = get_files(control)
        if not files:
            logger.info("Pas de nouveau document, arrêt.")
            continue
        recipient_list = [
            access.userprofile.user.email for access in control.access.all() if access.userprofile.send_files_report
        ]
        if not recipient_list:
            logger.info("Pas de destinataire, arrêt.")
            continue
        logger.debug(f"Destinataires : {len(recipient_list)}")
        date_cutoff = get_date_cutoff(control)
        context = {
            "control": control,
            "date_cutoff": date_cutoff.strftime("%A %d %B %Y"),
            "files": files,
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
                f"Il y avait {number_of_recipients} destinataires(s), et {number_of_sent_email} email(s) envoyé(s)."
            )
        if number_of_sent_email > 0:
            logger.info(f"Email envoyé pour le contrôle {control.id}")
            action.send(sender=control, verb=ACTION_LOG_REPORT_VERB_SENT)
        else:
            logger.info(f"Aucun email envoyé pour le contrôle {control.id}")
            action.send(sender=control, verb=ACTION_LOG_REPORT_VERB_NOT_SENT)

        EMAIL_SPACING_TIME_SECONDS = settings.EMAIL_SPACING_TIME_MILLIS / 1000
        logger.info(f"Attente de {EMAIL_SPACING_TIME_SECONDS}s après reporting pour le contrôle {control.id}")
        time.sleep(EMAIL_SPACING_TIME_SECONDS)


@app.task(queue=settings.CELERY_QUEUE)
def send_notifs_dates_echeances():
    html_template = "reporting/email/notif_date_echeance.html"
    text_template = "reporting/email/notif_date_echeance.txt"
    jours_echeance = Parametre.objects.filter(code="JOURS_ECHEANCE").filter(deleted_at__isnull=True).first()
    try:
        jours_echeance = int(jours_echeance.name)
    except Exception:
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
            recipient_list = [access.userprofile.user.email for access in questionnaire.control.access.all()]
            if not recipient_list:
                logger.info("Pas de destinataire, arrêt.")
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
                    f"Il y avait {number_of_recipients} destinataires(s), et {number_of_sent_email} email(s) envoyé(s)."
                )
            if number_of_sent_email > 0:
                logger.info(f"Email envoyé pour le questionnaire {questionnaire.id}")
                action.send(sender=questionnaire, verb=ACTION_LOG_DUE_VERB_SENT)
            else:
                logger.info(f"Aucun email envoyé pour le questionnaire {questionnaire.id}")
                action.send(sender=questionnaire, verb=ACTION_LOG_DUE_VERB_NOT_SENT)


@app.task(queue=settings.CELERY_QUEUE)
def identify_purgeable_controls(**kwargs):
    INTERVAL_PURGE = "interval_purge"
    ENVOI_NOTIF_MAIL = "envoi_notif_mail"
    INTERVAL_PURGE_REP_ORPH = "interval_purge_rep_orph"

    interval_purge_fr = kwargs.get(INTERVAL_PURGE, "").strip()
    envoi_notif_mail_fr = kwargs.get(ENVOI_NOTIF_MAIL, "").strip()
    interval_purge_rep_orph_fr = kwargs.get(INTERVAL_PURGE_REP_ORPH, "").strip()

    # Dictionnaires de mapping
    INTERVAL_MAP = {
        **{f"{i} mois": f"{i} month" if i == 1 else f"{i} months" for i in range(1, 13)},
        **{f"{i} an" + ("s" if i > 1 else ""): f"{i} year" + ("s" if i > 1 else "") for i in range(1, 6)},
    }
    VAL_ENVOI_NOTIF_MAIL_FR = {"Oui": True, "Non": False}

    interval_purge = INTERVAL_MAP.get(interval_purge_fr)
    interval_purge_rep_orph = INTERVAL_MAP.get(interval_purge_rep_orph_fr)
    envoi_notif_mail = VAL_ENVOI_NOTIF_MAIL_FR.get(envoi_notif_mail_fr, False)

    results_controls = []
    results_orphans = []

    logger.info(f"interval_purge (EN) = {interval_purge}")
    logger.info(f"envoi_notif_mail (EN) = {envoi_notif_mail}")
    logger.info(f"interval_purge_rep_orph (EN) = {interval_purge_rep_orph}")

    try:
        with connection.cursor() as cursor:
            cursor.callproc("identify_purgeable_controls", [interval_purge])
            results_controls = cursor.fetchall()

            if not results_controls:
                logger.info("Aucun espace de dépôt éligible à la suppression.")
            else:
                if envoi_notif_mail:
                    for mail_inspecteur, espaces_depot, _ in results_controls:
                        logger.info(f"Envoi mail à : {mail_inspecteur} pour espaces : {espaces_depot}")
                        send_mail_identify_purgeable_controls(mail_inspecteur, espaces_depot)

    except Exception as e:
        logger.error(f"Erreur lors de la procédure identify_purgeable_controls : {e}")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM identify_orphanuser(%s::INTERVAL)", [interval_purge_rep_orph])
            results_orphans = cursor.fetchall()

            if not results_orphans:
                logger.info("Aucun répondant éligible à la suppression.")

    except Exception as e:
        logger.error(f"Erreur lors de la procédure identify_orphanUser : {e}")

    return {"espaces_depot": results_controls, "repondants_orphelins": results_orphans}


@app.task(queue=settings.CELERY_QUEUE)
def logical_delete_controls():
    try:
        with connection.cursor() as cursor:
            cursor.callproc("logical_delete_controls")
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la procédure stockée : {e}")


@app.task(queue=settings.CELERY_QUEUE)
def physical_delete_controls():

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
            cursor.callproc("physical_delete_controls")
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la procédure stockée : {e}")


def collect_file_sizes():
    """
    Parcourt tous les fichiers de réponse stockés et regroupe leur taille
    par espace de dépôt (Control) et par questionnaire.
    """
    sizes_by_control = defaultdict(list)
    sizes_by_questionnaire = defaultdict(list)

    files = ResponseFile.objects.filter(is_deleted=False).select_related("question__theme__questionnaire__control")
    total_files = files.count()
    logger.info(f"Nombre de fichiers à analyser : {total_files}")

    for response_file in files.iterator():
        question = response_file.question
        if not question:
            continue
        questionnaire = question.questionnaire
        control = question.control
        if not questionnaire or not control:
            continue
        size = response_file.size
        sizes_by_control[control].append(size)
        sizes_by_questionnaire[questionnaire].append(size)

    return sizes_by_control, sizes_by_questionnaire


@app.task(queue=settings.CELERY_QUEUE)
def report_mean_file_size():
    """
    Log la taille moyenne des fichiers par espace de dépôt (Control) et par questionnaire.
    """
    logger.info("Démarrage du calcul de la taille moyenne des fichiers stockés.")

    sizes_by_control, sizes_by_questionnaire = collect_file_sizes()

    logger.info("=== Taille moyenne des fichiers par espace de dépôt ===")
    for control, sizes in sizes_by_control.items():
        avg_size = human_readable_size(mean(sizes))
        logger.info(
            f"Espace de dépôt [{control.reference_code}] {control.title_display} : "
            f"{len(sizes)} fichier(s), taille moyenne = {avg_size}"
        )

    logger.info("=== Taille moyenne des fichiers par questionnaire ===")
    for questionnaire, sizes in sizes_by_questionnaire.items():
        avg_size = human_readable_size(mean(sizes))
        logger.info(
            f"Questionnaire [{questionnaire.id}] {questionnaire.title} "
            f"(espace de dépôt {questionnaire.control.reference_code}) : "
            f"{len(sizes)} fichier(s), taille moyenne = {avg_size}"
        )

    if sizes_by_control:
        mean_control_size = human_readable_size(mean(sum(sizes) for sizes in sizes_by_control.values()))
        logger.info(
            f"Taille moyenne d'un espace de dépôt (toutes procédures confondues) : "
            f"{mean_control_size} ({len(sizes_by_control)} espace(s) de dépôt)"
        )
    else:
        logger.info("Aucun espace de dépôt avec fichiers, pas de taille moyenne calculable.")

    if sizes_by_questionnaire:
        mean_questionnaire_size = human_readable_size(mean(sum(sizes) for sizes in sizes_by_questionnaire.values()))
        logger.info(
            f"Taille moyenne d'un questionnaire (tous questionnaires confondus) : "
            f"{mean_questionnaire_size} ({len(sizes_by_questionnaire)} questionnaire(s))"
        )
    else:
        logger.info("Aucun questionnaire avec fichiers, pas de taille moyenne calculable.")

    logger.info("Fin du calcul de la taille moyenne des fichiers stockés.")


def get_disk_usage_report_dir():
    report_dir = os.path.join(settings.MEDIA_ROOT, DISK_USAGE_REPORT_DIRNAME)
    os.makedirs(report_dir, exist_ok=True)
    return report_dir


def get_disk_usage_report_path():
    """
    Retourne le chemin complet du dernier rapport de poids des fichiers généré,
    ou None si aucun rapport n'existe.
    """
    report_dir = get_disk_usage_report_dir()
    pattern = os.path.join(report_dir, f"{DISK_USAGE_REPORT_FILENAME_PREFIX}*.zip")
    existing_reports = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    return existing_reports[0] if existing_reports else None


def clear_disk_usage_reports():
    report_dir = get_disk_usage_report_dir()
    pattern = os.path.join(report_dir, f"{DISK_USAGE_REPORT_FILENAME_PREFIX}*.zip")
    for existing_report in glob.glob(pattern):
        try:
            os.remove(existing_report)
        except OSError as e:
            logger.error(f"Erreur lors de la suppression de l'ancien rapport {existing_report} : {e}")


@app.task(queue=settings.CELERY_QUEUE)
def generate_disk_usage_report_file():
    """
    Calcule le nombre de fichiers et la taille (totale et moyenne) des fichiers
    de réponse stockés, par espace de dépôt (Control) et par questionnaire, et
    écrit le résultat dans un fichier ZIP contenant deux CSV, dans le dossier
    `MEDIA_ROOT/rapports_poids_fichiers/`.

    Suprime les rapports précedents avant de générer le nouveau rapport.
    """
    logger.info("Démarrage de la génération du rapport de poids des fichiers.")

    sizes_by_control, sizes_by_questionnaire = collect_file_sizes()

    generation_date = date.today().strftime("%Y-%m-%d")
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zip_file:
        controls_csv_buffer = StringIO()
        controls_csv_writer = csv.writer(controls_csv_buffer, delimiter=";")
        controls_csv_writer.writerow([
            "id_espace_depot",
            "reference_code",
            "titre",
            "nombre_de_fichiers",
            "taille_totale_octets",
            "taille_moyenne_octets",
            "date_de_creation",
        ])
        for control, sizes in sizes_by_control.items():
            controls_csv_writer.writerow([
                control.id,
                control.reference_code,
                control.title,
                len(sizes),
                sum(sizes),
                round(mean(sizes)),
                control.created_date,
            ])
        zip_file.writestr(f"poids_fichiers_espaces_depot_{generation_date}.csv", controls_csv_buffer.getvalue())

        questionnaires_csv_buffer = StringIO()
        questionnaires_csv_writer = csv.writer(questionnaires_csv_buffer, delimiter=";")
        questionnaires_csv_writer.writerow([
            "id_questionnaire",
            "titre",
            "id_espace_depot",
            "reference_code_espace_depot",
            "nombre_de_fichiers",
            "taille_totale_octets",
            "taille_moyenne_octets",
            "date_de_creation",
            "date_derniere_action_fichier_reponse",
        ])
        for questionnaire, sizes in sizes_by_questionnaire.items():
            questionnaires_csv_writer.writerow([
                questionnaire.id,
                questionnaire.title,
                questionnaire.control.id,
                questionnaire.control.reference_code,
                len(sizes),
                sum(sizes),
                round(mean(sizes)),
                questionnaire.created_date,
                questionnaire.last_response_file_action,
            ])
        zip_file.writestr(f"poids_fichiers_questionnaires_{generation_date}.csv", questionnaires_csv_buffer.getvalue())

    clear_disk_usage_reports()

    report_dir = get_disk_usage_report_dir()
    report_path = os.path.join(report_dir, f"{DISK_USAGE_REPORT_FILENAME_PREFIX}{generation_date}.zip")
    with open(report_path, "wb") as report_file:
        report_file.write(zip_buffer.getvalue())

    logger.info(f"Rapport de poids des fichiers écrit : {report_path}")
    logger.info("Fin de la génération du rapport de poids des fichiers.")

    return report_path


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
