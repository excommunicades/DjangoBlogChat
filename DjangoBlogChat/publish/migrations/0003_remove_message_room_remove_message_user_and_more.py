# Generated by Django 5.1.4 on 2024-12-11 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publish', '0002_remove_chatroom_created_at_remove_chatroom_user1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='room',
        ),
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
        migrations.DeleteModel(
            name='ChatRoom',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]
