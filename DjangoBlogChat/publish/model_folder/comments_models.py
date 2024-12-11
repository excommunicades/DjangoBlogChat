from django.db import models

from publish.model_folder.posts_models import Posts


class Comments(models.Model):

    """Post's comments model"""

    post = models.ForeignKey(Posts, on_delete=models.CASCADE)

    owner = models.ForeignKey('blog_user.BlogUser', on_delete=models.CASCADE)

    content = models.TextField(blank=False, null=False)

    response = models.IntegerField(null=True, blank=True)

    is_blocked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class CommentReactions(models.Model):

    """Model about comment reactions as like, dislike, etc"""

    REACTION_CHOICES = [
        ('none', 'none'),
        ('like', 'like'),
        ('dislike', 'dislike'),
    ]

    comment = models.ForeignKey(Comments, on_delete=models.CASCADE)

    user = models.ForeignKey('blog_user.BlogUser', on_delete=models.CASCADE)

    reaction = models.CharField(
                            max_length=7,
                            choices=REACTION_CHOICES,
                            default='none')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
