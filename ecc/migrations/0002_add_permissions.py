from django.db import migrations
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.management import create_permissions
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

PERMISSIONS = [
                'add_faqitem',
                'change_faqitem',
                'delete_faqitem',
                'view_faqitem',
                'view_userprofile', 
	            'view_useripaddress',
                'view_cguitem',
                'add_cguitem',
                'change_cguitem',
                'delete_cguitem',
                'view_logentry', 
                'view_user', 
                'view_action', 
                'view_follow',
                'change_user',
                'view_control',
                'change_control',
                'view_question',
                'change_question',
                'add_questionfile', 
                'change_questionfile', 
                'delete_questionfile', 
                'view_questionfile', 
                'view_theme',
                'change_theme',
                'change_questionnaire',
                'add_crontabschedule',
                'change_crontabschedule',
                'delete_crontabschedule',
                'view_crontabschedule',
                'add_intervalschedule',
                'change_intervalschedule',
                'delete_intervalschedule',
                'view_intervalschedule',
                'add_periodictask',
                'change_periodictask',
                'delete_periodictask',
                'view_periodictask',
                'add_periodictasks',
                'change_periodictasks',
                'delete_periodictasks',
                'view_periodictasks',
                'add_solarschedule',
                'change_solarschedule',
                'delete_solarschedule',
                'view_solarschedule',
                'add_clockedschedule',
                'change_clockedschedule',
                'delete_clockedschedule',
                'view_clockedschedule',
                'change_site',
                'add_parametre',
                'change_parametre',
                'delete_parametre',
                'view_parametre',
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