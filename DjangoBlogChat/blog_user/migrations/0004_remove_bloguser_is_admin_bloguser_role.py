# Generated by Django 5.1.2 on 2024-11-18 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_user', '0003_bloguser_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bloguser',
            name='is_admin',
        ),
        migrations.AddField(
            model_name='bloguser',
            name='role',
            field=models.CharField(choices=[('user', 'User'), ('moderator', 'Moderator'), ('admin', 'Administrator')], default='user', max_length=10),
        ),
    ]
