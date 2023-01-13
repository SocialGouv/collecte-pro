from django.db import migrations
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.management import create_permissions
from django.conf import settings

PERMISSIONS = [
    # QuestionFile
    'add_questionfile', 'change_questionfile', 'delete_questionfile', 'view_questionfile',
]

def update_permissions(apps, schema_editor):
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
        ('ecc', '0004_update_permissions'),
    ]

    operations = [
        migrations.RunPython(update_permissions),
    ]
