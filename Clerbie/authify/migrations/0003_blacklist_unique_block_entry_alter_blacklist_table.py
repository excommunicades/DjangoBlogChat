# Generated by Django 5.1.4 on 2025-01-30 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authify', '0002_blacklist'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='blacklist',
            constraint=models.UniqueConstraint(fields=('user', 'blocked_user'), name='unique_block_entry'),
        ),
        migrations.AlterModelTable(
            name='blacklist',
            table='UserBlackList',
        ),
    ]
