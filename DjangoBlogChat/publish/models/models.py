import os

from django.db import models

# 'blog_user.BlogUser'
# upload_to=image_upload_function

def image_upload_function(instance, filename):

    model_name = instance.__class__.__name__.lower()

    if model_name == "posts":

        folder_name = "posts_images"

    else:
        folder_name = "other_images"

    safe_title = instance.title.replace(" ", "_").replace("/", "_")

    return os.path.join(folder_name, safe_title, filename)


class Posts(models.Model):

    """Model with cols for db table 'posts' """

    owner = models.ForeignKey('blog_user.BlogUser', on_delete=models.CASCADE)

    title = models.CharField(max_length=255, blank=False, null=False)

    content = models.TextField(blank=True, null=True)

    head_image = models.ImageField(upload_to=image_upload_function, blank=True, null=True)

    add_image_1 = models.ImageField(upload_to=image_upload_function, blank=True, null=True)

    add_image_2 = models.ImageField(upload_to=image_upload_function, blank=True, null=True)

    add_image_3 = models.ImageField(upload_to=image_upload_function, blank=True, null=True)

    add_image_4 = models.ImageField(upload_to=image_upload_function, blank=True, null=True)

    add_image_5 = models.ImageField(upload_to=image_upload_function, blank=True, null=True)
