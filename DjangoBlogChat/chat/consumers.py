import json
import redis

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from django.core.cache import cache


class PublicConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.user_id = self.scope['user'].id
        self.group_name = "public_room"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({

            "message": "You are connected to the public room!"

        }))

        await self.update_user_online_status(True)

    async def disconnect(self, close_code):

        await self.update_user_online_status(False)

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        pass

    async def chat_message(self, event):

        message = event['message']

        await self.send(text_data=json.dumps({

            'message': message

        }))

    async def update_user_online_status(self, online_status):

        user_status_key = f'user_{self.user_id}_status'
        
        cache.set(user_status_key, online_status, timeout=None)

    @staticmethod
    async def check_user_online_status(user_id):

        user_status_key = f"user_{user_id}_status"
        
        status = cache.get(user_status_key)

        return status
