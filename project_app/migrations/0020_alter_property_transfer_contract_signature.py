# Generated by Django 4.2.5 on 2023-10-26 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_app', '0019_property_transfer_contract_property_address_line_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property_transfer_contract',
            name='signature',
            field=models.CharField(default=None, max_length=512),
        ),
    ]