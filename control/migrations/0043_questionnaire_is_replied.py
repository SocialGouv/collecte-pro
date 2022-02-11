# Generated by Django 2.2.13 on 2021-08-02 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0042_auto_20211018_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='is_replied',
            field=models.BooleanField(default=False, help_text="Ce questionnaire a-t-il obtenu toutes les réponses de l'organisme contrôlé ?", verbose_name='répondu'),
        ),
    ]