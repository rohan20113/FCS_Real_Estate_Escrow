# Generated by Django 4.2.5 on 2023-10-01 17:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_app', '0008_alter_user_contact_alter_user_email_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='AppUser',
        ),
    ]
