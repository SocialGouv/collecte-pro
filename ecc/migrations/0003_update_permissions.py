from django.db import migrations
from django.contrib.auth.models import Permission, Group
from django.conf import settings

PERMISSIONS = [
    # QuestionFile
    'add_questionfile', 'change_questionfile', 'delete_questionfile', 'view_questionfile',
]

def update_permissions(apps, schema_editor):
    group = Group.objects.get_or_create(name='admin_metier')[0]
    for p in PERMISSIONS:
        permission = Permission.objects.get(codename=p)
        group.permissions.filter(id=permission.id).delete()
    group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ecc', '0002_add_permissions'),
    ]

    operations = [
        migrations.RunPython(update_permissions),
    ]