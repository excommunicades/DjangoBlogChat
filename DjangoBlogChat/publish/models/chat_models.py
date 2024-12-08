from django.db import models
from blog_user.models import BlogUser


class ChatRoom(models.Model):

    user1 = models.ForeignKey(BlogUser, related_name='user1', on_delete=models.CASCADE)

    user2 = models.ForeignKey(BlogUser, related_name='user2', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f'Chat beetween {self.user1.nickname} and {self.user2.nickname}'
