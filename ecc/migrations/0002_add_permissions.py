from django.db import migrations
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.management import create_permissions
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

PERMISSIONS = [
    # Action
    'view_action',
    # Celery tasks
    'add_crontabschedule', 'change_crontabschedule', 'delete_crontabschedule', 'view_crontabschedule',
    'add_intervalschedule', 'change_intervalschedule', 'delete_intervalschedule', 'view_intervalschedule',
    'add_periodictask', 'change_periodictask', 'delete_periodictask', 'view_periodictask',
    'add_periodictasks', 'change_periodictasks', 'delete_periodictasks', 'view_periodictasks',
    'add_solarschedule', 'change_solarschedule', 'delete_solarschedule', 'view_solarschedule',
    'add_clockedschedule', 'change_clockedschedule', 'delete_clockedschedule', 'view_clockedschedule',
    # CGU
    'add_cguitem', 'change_cguitem', 'delete_cguitem', 'view_cguitem',
    # Control
    'change_control', 'view_control',
    # FAQ
    'add_faqitem', 'change_faqitem', 'delete_faqitem', 'view_faqitem',
    # Follow
    'view_follow',
    # LogEntry
    'view_logentry',
    # Parametre
    'add_parametre', 'change_parametre', 'delete_parametre', 'view_parametre',
    # Question
    'change_question', 'view_question',
    # QuestionFile
    'add_questionfile', 'change_questionfile', 'delete_questionfile', 'view_questionfile',
    # Questionnaire
    'change_questionnaire',
    # Site
    'change_site',
    # Theme
    'change_theme', 'view_theme',
    # User
    'change_user', 'view_user',
    # UserIpAddress
    'view_useripaddress',
    # UserProfile
    'view_userprofile',
]

def add_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None

    group = Group.objects.get_or_create(name='admin_metier')[0]
    for p in PERMISSIONS:
        permission = Permission.objects.get(codename=p)
        group.permissions.add(permission)
    group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('actstream', '__latest__'),
        ('admin', '__latest__'),
        ('auth', '__latest__'),
        ('ecc', '0001_initial'),
        ('faq', '__latest__'),
        ('user_profiles', '__latest__'),
        ('tos', '__latest__'),
        ('control', '__latest__'),
        ('sites', '__latest__'),
        ('parametres', '__latest__'),
    ]

    operations = [
        migrations.RunPython(add_permissions),
    ]