# Generated by Django 2.2.22 on 2021-10-15 12:12

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0010_alter_group_name_max_length'),
    ]

    operations = [
        migrations.RunSQL("insert into auth_group values (nextval('auth_group_id_seq'), 'admin_metier');"),
    ]
