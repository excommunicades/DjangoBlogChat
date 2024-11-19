import os

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


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

    USER_ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Administrator'),
    ]

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

    avatar = models.ImageField(upload_to=image_upload_function, blank=True, null=True)

    is_actived = models.BooleanField(default=True)

    role = models.CharField(
                        max_length=10,
                        choices=USER_ROLE_CHOICES,
                        default='user'
                            )

    USERNAME_FIELD = 'nickname'

    objects = BlogUserManager()
