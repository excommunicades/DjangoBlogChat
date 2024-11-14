# Generated by Django 5.1.2 on 2024-11-14 17:30

import django.db.models.deletion
import publish.models.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True, null=True)),
                ('head_image', models.ImageField(blank=True, null=True, upload_to=publish.models.models.image_upload_function)),
                ('add_image_1', models.ImageField(blank=True, null=True, upload_to=publish.models.models.image_upload_function)),
                ('add_image_2', models.ImageField(blank=True, null=True, upload_to=publish.models.models.image_upload_function)),
                ('add_image_3', models.ImageField(blank=True, null=True, upload_to=publish.models.models.image_upload_function)),
                ('add_image_4', models.ImageField(blank=True, null=True, upload_to=publish.models.models.image_upload_function)),
                ('add_image_5', models.ImageField(blank=True, null=True, upload_to=publish.models.models.image_upload_function)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
