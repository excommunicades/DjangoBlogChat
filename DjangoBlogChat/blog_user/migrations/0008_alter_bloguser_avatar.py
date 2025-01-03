# Generated by Django 5.1.4 on 2025-01-01 14:22

import blog_user.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_user', '0007_alter_bloguser_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bloguser',
            name='avatar',
            field=models.ImageField(default='default/default_avatar.png', upload_to=blog_user.models.image_upload_function),
        ),
    ]
