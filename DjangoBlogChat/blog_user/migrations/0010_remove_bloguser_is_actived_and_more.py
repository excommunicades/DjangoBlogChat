# Generated by Django 5.1.4 on 2025-01-01 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog_user', '0009_bloguser_behavior_points_bloguser_birthday_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bloguser',
            name='is_actived',
        ),
        migrations.RemoveField(
            model_name='bloguser',
            name='is_blocked',
        ),
    ]
