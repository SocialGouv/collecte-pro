# Generated by Django 2.2.22 on 2021-10-25 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0003_auto_20211022_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametre',
            name='nom',
        ),
        migrations.RemoveField(
            model_name='parametre',
            name='ordre',
        ),
        migrations.AddField(
            model_name='parametre',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='name'),
        ),
    ]
