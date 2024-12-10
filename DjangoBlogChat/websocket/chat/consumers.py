from datetime import datetime
import json
import redis

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from django.core.cache import cache

from publish.models.chat_models import (
    ChatRoom,
    ChatMessages,
)

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


# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):

#         user_1 = self.scope['url_route']['kwargs']['user1']
#         user_2 = self.scope['url_route']['kwargs']['user2']

#         room_name = f'chat_{min(int(user_1), int(user_2))}_{max(int(user_1), int(user_2))}'

#         print(user_1, user_2)

#         # MODELS

#         # class Chat(models.Model):
#         # name = models.CharField(max_length=255, unique=True)
#         # participants = models.ManyToManyField(User)
#         # created_at = models.DateTimeField(auto_now_add=True)

#         # def __str__(self):
#         #     return self.name

#         # chat, created = Chat.objects.get_or_create(name=room_name)

#         #     if user_1 not in chat.participants.all():

#         #         chat.participants.add(user_1)

#         #     if user_2 not in chat.participants.all():

#         #         chat.participants.add(user_2)

#         #     chat.save()

#         self.room_group_name = room_name

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):

#         await self.channel_layer.discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):

#         text_data_json = json.loads(text_data)

#         message = text_data_json['message']

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type": "chat_message",
#                 "message": message,
#                 "sender": self.scope['user'].nickname,
#             }
#         )

#         # user = self.scope["user"]
#         # chat = Chat.objects.get(name=self.room_group_name)
        
#         # message = Message.objects.create(
#         #     chat=chat,
#         #     sender=user,
#         #     content=text_data
#         # )

#         # Отправка всем пользователям чата (Future)

#         # await self.channel_layer.group_send(
#         #     self.room_group_name,
#         #     {
#         #         'type': 'chat_message',
#         #         'message': message.content,
#         #         'sender': user.username
#         #     }
#         # )


#     async  def send_chat_message(self, event):

#         message = event['message']

#         sender = event['sender']

#         await self.send(text_data=json.dumps({
#             'message': message,
#             'sender': sender
#         }))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_1 = self.scope['url_route']['kwargs']['user1']
        user_2 = self.scope['url_route']['kwargs']['user2']

        room_name = f'chat_{min(int(user_1), int(user_2))}_{max(int(user_1), int(user_2))}'
        
        self.room_group_name = room_name

        if ChatRoom.objects.filter(room_name)

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
