import os
import uuid
from datetime import datetime
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from authify.choices import (
    COUNTRIES,
    TIME_ZONES,
    GENDER_CHOICES,
    USER_ROLE_CHOICES,
    ACCOUNT_STATUS_CHOICES,
    PROGRAMMING_ROLES_CHOICES,
)

def image_upload_function(instance, filename):

    model_name = instance.__class__.__name__.lower()

    if model_name == "Clerbie":
        folder_name = "users_avatars"

    elif model_name == "ClerbieManager":
        folder_name = "users_avatars"

    else:
        folder_name = "other_images"

    safe_title = instance.nickname.replace(" ", "_").replace("/", "_")

    return os.path.join(folder_name, safe_title, filename)


class ClerbieManager(BaseUserManager):

    def get_by_natural_key(self, nickname):
        return self.get(nickname=nickname)

    def create_user(self, username, email, password=None, **extra_fields):

        if not email:
            raise ValueError('User must have email')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Clerbie(AbstractBaseUser, PermissionsMixin):

    """Blog user model"""

    username = models.CharField(
                            max_length=30,
                            blank= False,
                            null=False,
                            )

    nickname = models.CharField(
                            max_length=30,
                            blank= False,
                            null=False,
                            unique=True,
                            )
    email = models.EmailField(
                        unique=True,
                        blank=False,
                        null=False,
                        )

    password = models.CharField(
                            max_length=128,
                            blank=False,
                            null=False,
                            )

    role = models.CharField(
                        max_length=10,
                        choices=USER_ROLE_CHOICES,
                        default='user'
                            )

    gender = models.CharField(
                        max_length=6,
                        choices=GENDER_CHOICES,
                        default='other')

    about_me = models.TextField(max_length=50000, blank=True, null=True)
    technologies = models.ManyToManyField('profile.Technologies', blank=True, related_name='user_techonlogies')

    behavior_points = models.IntegerField(default=1000)
    registered_at = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to=image_upload_function, default='default/default_avatar.png')

    birthday = models.DateField(blank=True, null=True)
    country = models.CharField(default='None', choices=COUNTRIES)
    phone_number = phone_number = PhoneNumberField(blank=True, null=True)
    time_zones = models.CharField(default='UTC+00:00',choices=TIME_ZONES)
    status = models.CharField(max_length=10, default='ACTIVE', choices=ACCOUNT_STATUS_CHOICES)

    github = models.URLField(max_length=200, blank=True, null=True)
    skype = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    youtube = models.URLField(max_length=200, blank=True, null=True)
    discord = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    telegram = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)

    business_email = models.EmailField(max_length=100, blank=True,null=True)

    job_title = models.CharField(
        default='None',
        max_length=40,
        choices=PROGRAMMING_ROLES_CHOICES,
        blank=True,
        null=True,
    )

    two_factor_method = models.CharField(
        default='disabled',
        max_length=50, 
        choices=[('enabled', 'Enabled'), ('disabled', 'Disabled')],
        blank=True, 
        null=True
    )


    USERNAME_FIELD = 'nickname'

    objects = ClerbieManager()

    last_activity = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'UserProfile'


class BlackList(models.Model):

    ''' BlackList functionallity model '''

    user = models.ForeignKey('Clerbie', on_delete=models.CASCADE, related_name='blocklist_users')
    blocked_user = models.ForeignKey('Clerbie', on_delete=models.CASCADE, related_name='blocked_by_users')
    blocked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'UserBlackList'
        constraints = [
            models.UniqueConstraint(fields=['user', 'blocked_user'], name='unique_block_entry')
        ]