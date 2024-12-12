import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

connected_users = {}

class CommunityConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        query_params = dict(param.split('=') for param in self.scope['query_string'].decode().split('&'))
        

        self.user_id = query_params.get('userId')

        if not self.user_id:
            await self.close()
            return

        self.user_id = int(self.user_id)

        self.room_group_name = f'community'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        connected_users[self] = self.user_id

        await self.accept()

    async def disconnect(self, close_code):

        if self.user_id in connected_users:
            del connected_users[self.user_id]

        for user_id, user in connected_users.items():
            print(f'User disconnected:', self.user_id)
            await user.send(text_data=json.dumps({
                'message': f'User disconnected: {self.user_id}'
            }))

    async def receive(self, text_data):

        message = json.loads(text_data).get('message', '')

        for user_id, user in connected_users.items():
            await user.send(text_data=json.dumps({
                'message': f'User {self.user_id}: {message}'
            }))


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        query_params = dict(param.split('=') for param in self.scope['query_string'].decode().split('&'))
        

        self.user_id = query_params.get('userId')

        if not self.user_id:
            await self.close()
            return


        self.chat_name = self.scope['url_route']['kwargs']['chat_name']

        self.room_group_name = f'chat_{self.chat_name}'

        self.chat_room = await self.create_chat()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.add_user_to_chat()

        await self.accept()

    async def disconnect(self, close_code):

        await self.remove_user_from_chat()

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):

        text_data_json = json.loads(text_data)


        message = text_data_json.get('message')

        if message:

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    async def chat_message(self, event):

        message = event['message']


        await self.send(text_data=json.dumps({
            'message': message
        }))


    @database_sync_to_async
    def create_chat(self):
        from publish.models import ChatRoom
        try:

            chat = ChatRoom.objects.get(name=str(self.room_group_name))
        except ChatRoom.DoesNotExist:

            chat = ChatRoom.objects.create(
                name=str(self.room_group_name),
            )
        return chat


    @database_sync_to_async
    def add_user_to_chat(self):
        chat_room = self.chat_room
        user = int(self.user_id)

        if user and user not in chat_room.users.all():

            chat_room.users.add(user)


    @database_sync_to_async
    def remove_user_from_chat(self):
        chat_room = self.chat_room
        user = int(self.user_id)

        if user and user in chat_room.users.all():

            chat_room.users.remove(user)


    @database_sync_to_async
    def get_user_by_id(self, user_id):
        from blog_user.models import BlogUser
        try:
            user = BlogUser.objects.get(id=user_id)
            return user
        except BlogUser.DoesNotExist:
            return None
