# Generated by Django 5.1.4 on 2025-02-11 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0007_remove_clerbie_education_created_at_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Education',
            new_name='University',
        ),
    ]
