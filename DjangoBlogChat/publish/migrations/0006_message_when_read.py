# Generated by Django 5.1.4 on 2024-12-19 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publish', '0005_message_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='when_read',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]