import json
import hashlib

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from django.db import IntegrityError

connected_users = {}

@database_sync_to_async
def get_user_by_id(user_id):

    from blog_user.models import BlogUser

    try:

        return BlogUser.objects.get(id=user_id)

    except BlogUser.DoesNotExist:

        return None

# class CommunityConsumer(AsyncWebsocketConsumer):

#     async def connect(self):

#         query_params = dict(param.split('=') for param in self.scope['query_string'].decode().split('&'))
        

#         self.user_id = query_params.get('userId')

#         if not self.user_id:
#             await self.close()
#             return

#         self.user_id = int(self.user_id)

#         self.room_group_name = f'community'

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name,
#         )

#         connected_users[self.user_id] = self

#         await self.accept()

#         user_ids = ",".join(str(user_id) for user_id in connected_users.keys())


#         for user_id, user in connected_users.items():
#             print(f'User connected: {self.user_id}, All users: {user_ids}')
#             await user.send(text_data=json.dumps({
#                 'message': f'User connected: {self.user_id}. All users: {user_ids}'
#             }))

#     async def disconnect(self, close_code):

#         if self.user_id in connected_users:
#             del connected_users[self.user_id]

#         user_ids = ",".join(str(user_id) for user_id in connected_users.keys())

#         for user_id, user in connected_users.items():
#             print(f'User disconnected: {self.user_id}, All users: {user_ids}')
#             await user.send(text_data=json.dumps({
#                 'message': f'User disconnected: {self.user_id}. All users: {user_ids}'
#             }))

#     async def receive(self, text_data):

#         message = json.loads(text_data).get('message', '')

#         for user_id, user in connected_users.items():
#             await user.send(text_data=json.dumps({
#                 'message': f'User {self.user_id}: {message}'
#             }))


# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):

#         query_params = dict(param.split('=') for param in self.scope['query_string'].decode().split('&'))
        

#         self.user_id = query_params.get('userId')

#         if not self.user_id:
#             await self.close()
#             return


#         self.chat_name = self.scope['url_route']['kwargs']['chat_name']

#         self.room_group_name = f'chat_{self.chat_name}'

#         self.chat_room = await self.create_chat()

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name,
#         )

#         await self.add_user_to_chat()

#         await self.accept()

#     async def disconnect(self, close_code):

#         await self.remove_user_from_chat()

#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name,
#         )

#     async def receive(self, text_data):

#         text_data_json = json.loads(text_data)
#         message = text_data_json.get('message')

#         if message:

#             user = await get_user_by_id(int(self.user_id))

#             if user:
#                 print('user is est', user)
#                 await self.save_message(user, self.chat_room, message)

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'chat_message',
#                     'message': message
#                 }
#             )

#     async def chat_message(self, event):

#         message = event['message']


#         await self.send(text_data=json.dumps({
#             'message': message
#         }))


#     @database_sync_to_async
#     def create_chat(self):
#         from publish.models import ChatRoom
#         try:

#             chat = ChatRoom.objects.get(name=str(self.room_group_name))
#         except ChatRoom.DoesNotExist:

#             chat = ChatRoom.objects.create(
#                 name=str(self.room_group_name),
#             )
#         return chat


#     @database_sync_to_async
#     def add_user_to_chat(self):
#         chat_room = self.chat_room
#         user = int(self.user_id)

#         if user and user not in chat_room.users.all():

#             chat_room.users.add(user)


#     @database_sync_to_async
#     def remove_user_from_chat(self):
#         chat_room = self.chat_room
#         user = int(self.user_id)

#         if user and user in chat_room.users.all():

#             chat_room.users.remove(user)


#     @database_sync_to_async
#     def save_message(self, user, chat_room, message):

#         from publish.models import Message

#         Message.objects.create(
#             user=user,
#             room=chat_room,
#             content=message,
#         )


# class CommunityConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         # Отримуємо параметри запиту, зокрема userId
#         query_params = dict(param.split('=') for param in self.scope['query_string'].decode().split('&'))
#         self.user_id = query_params.get('userId')

#         if not self.user_id:
#             await self.close()
#             return

#         self.user_id = int(self.user_id)
#         self.current_chat_name = None  # Поточний активний чат
#         self.room_group_name = f'community'  # Основна група для оновлення статусу онлайн/офлайн

#         # Додаємо користувача до групи "community"
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         connected_users[self.user_id] = self  # Додаємо користувача до словника активних з'єднань

#         await self.accept()

#         await self.broadcast_user_status('online')

#     async def disconnect(self, close_code):
#         # Видаляємо користувача з підключених користувачів
#         if self.user_id in connected_users:
#             del connected_users[self.user_id]

#         # Видаляємо користувача з поточного чату
#         if self.current_chat_name:
#             await self.channel_layer.group_discard(f'chat_{self.current_chat_name}', self.channel_name)

#         # Видаляємо користувача з групи "community"
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#         await self.broadcast_user_status('offline')

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         action = data.get('action')

#         if action == 'switch_chat':
#             new_chat_name = data.get('chat_name')

#             # Відключаємо користувача від попередньої групи чату
#             if self.current_chat_name:
#                 await self.channel_layer.group_discard(f'chat_{self.current_chat_name}', self.channel_name)

#             self.current_chat_name = new_chat_name

#             # Додаємо користувача до нової групи чату
#             await self.channel_layer.group_add(f'chat_{new_chat_name}', self.channel_name)

#         elif action == 'send_message':
#             message = data.get('message')
#             await self.channel_layer.group_send(
#                 f'chat_{self.current_chat_name}',
#                 {
#                     'type': 'chat_message',
#                     'user_id': self.user_id,
#                     'message': message
#                 }
#             )

#         elif action == 'user_active':
#             await self.broadcast_user_status('active')

#         elif action == 'user_idle':
#             await self.broadcast_user_status('idle')

#     async def chat_message(self, event):
#         """
#         Відправляємо повідомлення всім користувачам у поточному чаті
#         """
#         await self.send(text_data=json.dumps({
#             'type': 'chat_message',
#             'user_id': event['user_id'],
#             'message': event['message']
#         }))

#     async def broadcast_user_status(self, status):
#         """
#         Відправляємо оновлення статусу користувача у спільну групу (online, offline, idle, active)
#         """
#         user_ids = list(connected_users.keys())
#         for user_id, user in connected_users.items():
#             await user.send(text_data=json.dumps({
#                 'type': 'user_status',
#                 'user_id': self.user_id,
#                 'status': status,
#                 'online_users': user_ids  # Надсилаємо список всіх активних користувачів
#             }))



class CommunityConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        query_params = dict(param.split('=') for param in self.scope['query_string'].decode().split('&'))
        self.user_id = query_params.get('userId')

        if not self.user_id:
            await self.close()
            return

        self.user_id = int(self.user_id)
        self.room_group_name = f'community'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        connected_users[self.user_id] = self

        await self.accept()

    async def disconnect(self, close_code):

        if self.user_id in connected_users:
            del connected_users[self.user_id]

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):

        data = json.loads(text_data)
        action = data.get('type')

        if action == 'chat_message':

            participants = data.get('participants').split(',')
            sender_id = int(data.get('sender'))
            message = data.get('message')

            participants_ids = list(map(int, participants))

            participants_ids.sort()

            chat_name = f"chat_{'_'.join(map(str, participants_ids))}"

            chat_hash = hashlib.sha256(chat_name.encode('utf-8')).hexdigest()

            for participant_id in participants_ids:

                participant_channel = connected_users.get(participant_id)

                user = await get_user_by_id(int(participant_id))

                await self.add_user_to_chat(chat_name=chat_hash, user=user)
                
                if participant_channel:
                    await participant_channel.send(text_data=json.dumps({
                        'type': 'chat_message',
                        'user_id': sender_id,
                        'message': message
                    }))

            user = await get_user_by_id(int(self.user_id))

            await self.save_message_to_chat(chat_hash, user, message)


    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'user_id': event['user_id'],
            'message': event['message']
        }))


    @database_sync_to_async
    def add_user_to_chat(self, chat_name, user):

        from publish.models import ChatRoom

        chat, created = ChatRoom.objects.get_or_create(name=chat_name)

        if user not in chat.users.values_list('id', flat=True):
            chat.users.add(user)

        return chat


    @database_sync_to_async
    def save_message_to_chat(self, chat_name, user, message):

        from publish.models import ChatRoom, Message

        chat = ChatRoom.objects.get(name=chat_name)

        Message.objects.create(
            user=user,
            room=chat,
            content=message
        )
