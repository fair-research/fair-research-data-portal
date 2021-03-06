# Generated by Django 2.0.6 on 2018-09-07 20:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('portal', '0005_auto_20180821_1909'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Workflow',
            new_name='Workspace',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='workflow',
            new_name='workspace',
        ),
        migrations.AlterField(
            model_name='task',
            name='category',
            field=models.CharField(choices=[('JUPYTERHUB', 'Jupyterhub'),
                                            ('WES', 'WES')], max_length=128),
        ),
    ]
