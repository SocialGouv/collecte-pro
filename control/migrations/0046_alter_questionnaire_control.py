# Generated by Django 3.2.7 on 2022-02-07 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0045_alter_questionnaire_is_replied'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='control',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questionnaires', to='control.control', verbose_name='procédure'),
        ),
    ]
