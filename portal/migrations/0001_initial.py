# Generated by Django 2.0.6 on 2018-06-26 03:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('search', '0002_auto_20180625_1427'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('globus_genomics_apikey', models.CharField(max_length=128)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('category', models.CharField(choices=[('GLOBUS_GENOMICS', 'Globus Genomics'), ('JUPYTERHUB', 'Jupyterhub')], max_length=128)),
                ('data_store', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('WAITING', 'Waiting'), ('READY', 'Ready'), ('RUNNING', 'Running'), ('COMPLETE', 'Complete'), ('ERROR', 'Error')], max_length=64)),
                ('description', models.CharField(blank=True, max_length=128)),
                ('input', models.ManyToManyField(blank=True, related_name='minid_input', to='search.Minid')),
                ('output', models.ManyToManyField(blank=True, related_name='minid_output', to='search.Minid')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.Workflow'),
        ),
    ]
