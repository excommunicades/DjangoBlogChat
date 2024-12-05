import json
import redis

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from django.core.cache import cache


class PublicConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        for value in self.scope.values():

            if isinstance(value, bytes) and b'userId=' in value:

                user_id_str = value.decode('utf-8')

                userId = user_id_str.split('=')[1]

                print(f'Extracted userId: {userId}')

                break
        else:

            userId = None

        if not userId:

            print('userId not found. Denying connection.')

            await self.close(code=4000)

            return


        self.user_id = userId

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
