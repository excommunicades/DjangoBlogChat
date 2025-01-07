# Generated by Django 5.1.4 on 2025-01-07 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog_user', '0012_alter_work_table'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='bloguser_friends',
            name='unique_friendship',
        ),
        migrations.AlterModelTable(
            name='bloguser',
            table='UserProfile',
        ),
        migrations.AlterModelTable(
            name='bloguser_certificates',
            table='UserCertificates',
        ),
        migrations.AlterModelTable(
            name='bloguser_education',
            table='UserEducations',
        ),
        migrations.AlterModelTable(
            name='bloguser_friends',
            table='UserFriends',
        ),
        migrations.AlterModelTable(
            name='bloguser_hobbies',
            table='UserHobbies',
        ),
        migrations.AlterModelTable(
            name='bloguser_reactions',
            table='UserReactions',
        ),
        migrations.AlterModelTable(
            name='certificates',
            table='Certificates',
        ),
        migrations.AlterModelTable(
            name='education',
            table='Educations',
        ),
        migrations.AlterModelTable(
            name='hobby',
            table='Hobbies',
        ),
        migrations.AlterModelTable(
            name='projects',
            table='Projects',
        ),
        migrations.AlterModelTable(
            name='technologies',
            table='Technologies',
        ),
        migrations.AlterModelTable(
            name='userworkexperience',
            table='UserWorks',
        ),
    ]
