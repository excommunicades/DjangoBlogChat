import os
from datetime import datetime

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

from blog_user.choices import (
    USER_ROLE_CHOICES,
    GENDER_CHOICES,
    COUNTRIES,
    TIME_ZONES,
    ACCOUNT_STATUS_CHOICES,
    PROGRAMMING_ROLES_CHOICES,
)


def image_upload_function(instance, filename):

    model_name = instance.__class__.__name__.lower()

    if model_name == "BlogUser":

        folder_name = "users_avatars"

    elif model_name == "BlogUserManager":

        folder_name = "users_avatars"

    else:
        folder_name = "other_images"

    safe_title = instance.title.replace(" ", "_").replace("/", "_")

    return os.path.join(folder_name, safe_title, filename)


class BlogUserManager(BaseUserManager):

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


class BlogUser(AbstractBaseUser, PermissionsMixin):

    """Blog user model"""

    # first_name = models.CharField(max_length=30, blank=False, null=False)
    # last_name = models.CharField(max_length=30, blank=False, null=False)

    # TODO (other tables): WORK EXPERIENCE, PROJECTS, CERTIFICATES, LICENSES, EDUCATION, LIKES, DISLIKES, HOBBY, FRIENDS, LAST ACTIVITY, REVIEWS

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

    avatar = models.ImageField(upload_to=image_upload_function, default='default/default_avatar.png')

    registered_at = models.DateTimeField(auto_now_add=True)

    role = models.CharField(
                        max_length=10,
                        choices=USER_ROLE_CHOICES,
                        default='user'
                            )

    behavior_points = models.IntegerField(default=1000)

    gender = models.CharField(
                        max_length=6,
                        choices=GENDER_CHOICES,
                        default='other')

    birthday = models.DateField(blank=True, null=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)

    country = models.CharField(default='None', choices=COUNTRIES)

    time_zones = models.CharField(default='UTC+00:00',choices=TIME_ZONES)

    status = models.CharField(max_length=10, default='ACTIVE', choices=ACCOUNT_STATUS_CHOICES)

    telegram = models.CharField(max_length=100, blank=True, null=True)
    whatsapp = models.CharField(max_length=100, blank=True, null=True)
    viber = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    github = models.URLField(max_length=200, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    skype = models.CharField(max_length=100, blank=True, null=True)
    discord = models.CharField(max_length=100, blank=True, null=True)
    dou = models.CharField(max_length=100, blank=True, null=True)
    djinni = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    youtube = models.URLField(max_length=200, blank=True, null=True)
    pinterest = models.URLField(max_length=200, blank=True, null=True)
    tiktok = models.CharField(max_length=100, blank=True, null=True)
    reddit = models.CharField(max_length=100, blank=True, null=True)
    snapchat = models.CharField(max_length=100, blank=True, null=True)

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

    objects = BlogUserManager()
