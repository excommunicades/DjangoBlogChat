# Generated by Django 5.1.4 on 2025-02-13 08:42

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0012_alter_companies_table'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserWorkExperience',
            new_name='UserJobExperience',
        ),
    ]
