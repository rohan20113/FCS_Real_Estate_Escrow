# Generated by Django 4.2.5 on 2023-10-31 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_app', '0027_rentalscontract_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rentalscontract',
            name='party_type',
            field=models.CharField(default=False, max_length=6),
        ),
    ]