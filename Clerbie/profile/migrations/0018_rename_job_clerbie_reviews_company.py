# Generated by Django 5.1.4 on 2025-02-18 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0017_rename_job_experience_clerbie_reviews_job'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clerbie_reviews',
            old_name='job',
            new_name='company',
        ),
    ]
