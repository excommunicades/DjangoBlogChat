# Generated by Django 5.1.4 on 2025-02-04 16:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0005_remove_clerbie_hobbies_created_timestamp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clerbie_friends',
            old_name='user',
            new_name='user1',
        ),
        migrations.RenameField(
            model_name='clerbie_friends',
            old_name='friend',
            new_name='user2',
        ),
    ]
