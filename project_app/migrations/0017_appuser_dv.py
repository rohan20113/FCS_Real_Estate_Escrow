# Generated by Django 4.2.5 on 2023-10-25 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_app', '0016_remove_property_lessee'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='dv',
            field=models.BooleanField(default=False),
        ),
    ]
