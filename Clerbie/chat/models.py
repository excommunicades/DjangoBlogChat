from django.db import models

from authify.models import Clerbie


class ChatRoom(models.Model):
    
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(Clerbie, related_name='chat_rooms')


    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Chats'


class Message(models.Model):

    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Clerbie, on_delete=models.CASCADE)
    when_read = models.DateTimeField(blank=True, null=True)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    reply_to = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    reply_from = models.ForeignKey(Clerbie, on_delete=models.CASCADE, null=True, blank=True, related_name='reply_owners')
    status = models.CharField(default='delivered', choices=[('delivered', 'Delivered'), ('read', 'Read')], max_length=10)


    def __str__(self):
        return f'{self.user.username}: {self.content[:30]}'

    class Meta:
        db_table = 'ChatMessages'