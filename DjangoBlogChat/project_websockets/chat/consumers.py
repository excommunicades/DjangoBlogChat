from datetime import datetime
import json
import redis

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from django.core.cache import cache

# from publish.models.chat_models import (
#     ChatRoom,
#     ChatMessages,
# )

class ChatNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.user_id = self.scope['url_route']['kwargs']['user_id']

        self.group_name = f'chat_notifications_{self.user_id}'

        await self.accept()

        await self.send(text_data=json.dumps({

            "message": f"User {self.user_id} connected to {self.group_name}"

        }))

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print(f"Message from {self.user_id}: {message}")


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_1 = self.scope['url_route']['kwargs']['user1']
        user_2 = self.scope['url_route']['kwargs']['user2']

        room_name = f'chat_{min(int(user_1), int(user_2))}_{max(int(user_1), int(user_2))}'
        
        self.room_group_name = room_name

        try:

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

        except Exception as e:

            print(f"Connection error-: {e}")

            await self.close()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        sender = text_data_json['senderId']
        message = text_data_json['message']
        message_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print('receive_',text_data_json['senderId'])

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'time': message_time,

            }
        )

    async def chat_message(self, event):
        print(event)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'time':  event['time'],
        }))
