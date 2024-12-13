from django.db import models

from blog_user.models import BlogUser


class ChatRoom(models.Model):
    
    name = models.CharField(max_length=100)

    users = models.ManyToManyField(BlogUser, related_name='chat_rooms')


    def __str__(self):
        return self.name




class Message(models.Model):

    user = models.ForeignKey(BlogUser, on_delete=models.CASCADE)

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')

    content = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user.username}: {self.content[:30]}'