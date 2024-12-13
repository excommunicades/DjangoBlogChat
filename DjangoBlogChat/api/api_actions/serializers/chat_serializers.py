from rest_framework import serializers

from blog_user.models import BlogUser
from publish.models import ChatRoom, Message


class ChatListSerializer(serializers.ModelField):

    class Meta:

        model = ChatRoom

        fields = [
            'id',
            'name',
        ]
        