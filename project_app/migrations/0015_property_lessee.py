# Generated by Django 4.2.5 on 2023-10-15 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_app', '0014_alter_appuser_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='lessee',
            field=models.CharField(blank=True, default=None, max_length=30, null=True),
        ),
    ]
