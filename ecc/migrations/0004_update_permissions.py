from django.db import migrations
from django.contrib.auth.models import Permission, Group
from django.conf import settings

PERMISSIONS = [
    # Access
    'add_access', 'change_access', 'delete_access', 'view_access',
    # Alert
    'add_alert', 'change_alert', 'delete_alert', 'view_alert',
    # QuestionnaireFile
    'add_questionnairefile', 'change_questionnairefile', 'delete_questionnairefile', 'view_questionnairefile',
]

def update_permissions(apps, schema_editor):
    group = Group.objects.get_or_create(name='admin_metier')[0]
    for p in PERMISSIONS:
        permission = Permission.objects.get(codename=p)
        group.permissions.add(permission)
    group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ecc', '0003_update_permissions'),
    ]

    operations = [
        migrations.RunPython(update_permissions),
    ]
