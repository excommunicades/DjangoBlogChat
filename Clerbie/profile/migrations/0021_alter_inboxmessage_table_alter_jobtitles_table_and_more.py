# Generated by Django 5.1.4 on 2025-02-20 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0020_jobtitles'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='inboxmessage',
            table='InboxMessages',
        ),
        migrations.AlterModelTable(
            name='jobtitles',
            table='JobTitles',
        ),
        migrations.AlterModelTable(
            name='university',
            table='Universities',
        ),
        migrations.AlterModelTable(
            name='userjobexperience',
            table='UserJobs',
        ),
    ]
