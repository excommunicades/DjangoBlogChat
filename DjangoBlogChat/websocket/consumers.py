from datetime import datetime
import asyncio
import json
import hashlib

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from django.db import IntegrityError
from django.db.models import Max

connected_users = {}

@database_sync_to_async
def get_user_by_id(user_id):

    from blog_user.models import BlogUser

    try:

        return BlogUser.objects.get(id=user_id)

    except BlogUser.DoesNotExist:

        return None


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
            sender_name = str(data.get('sender_name'))
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
                        'sender_id': sender_id,
                        'username': sender_name,
                        'message': message,
                    }))

            user = await get_user_by_id(int(self.user_id))

            await self.save_message_to_chat(chat_hash, user, message)

        elif action == 'get_chat_list':

            user_chats = await self.get_user_chats(self.user_id)

            await self.send(text_data=json.dumps({
                'type': 'chat_list',
                'chats': user_chats
            }))

        elif action == 'get_chat_messages':

            chat_id = data.get('chat_id')

            messages = await self.get_chat_messages(chat_id)

            await self.send(text_data=json.dumps({
                'type': 'chat_messages',
                'messages': messages
            }))

        elif action == 'delete_chat_message':

            message_id = data.get('message_id')

            await self.send_delete_message(message_id=message_id,user=self.user_id)

        elif action == 'update_chat_message':

            message_id = data.get('message_id')
            
            new_message_content = data.get('new_message_content')

            await self.send_update_message(message_id=message_id, user=self.user_id, new_message_content=new_message_content)


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

    @database_sync_to_async
    def get_user_chats(self, user_id):

        from publish.models import ChatRoom

        chats = ChatRoom.objects.filter(users__id=user_id)

        chats = chats.annotate(last_message_time=Max('messages__timestamp'))

        chats = chats.order_by('-last_message_time')

        chat_list = []

        for chat in chats:

            users_in_chat = chat.users.exclude(id=user_id)
            
            user_names = [user.username for user in users_in_chat]

            chat_users = ', '.join(user_names)

            last_message_time = chat.last_message_time.isoformat() if chat.last_message_time else None

            chat_list.append({
                'chat_users': chat_users,
                'chat_id': chat.id,
                'last_message_time': last_message_time
            })

        return chat_list


    @database_sync_to_async
    def get_chat_messages(self, chat_id):

        from publish.models import Message

        messages = Message.objects.filter(room_id=chat_id).select_related('user').order_by('-timestamp')

        message_list = [{
                'message_id': message.id,
                'user_id': message.user.id,
                'username': message.user.username,
                'message': message.content,
                'timestamp': message.timestamp.isoformat()} for message in messages]

        return message_list


    @database_sync_to_async
    def delete_message(self,message_id, user):

        from publish.models import Message

        message = Message.objects.filter(id=message_id).first()

        if message and message.user.id == int(user):

            chat = message.room
            message.delete()

            participants = chat.users.all()

            participants_id_list = []

            for participant in participants:

                if connected_users.get(participant.id) is not None:

                    participants_id_list.append(connected_users.get(participant.id))

        return participants_id_list

    async def send_delete_message(self, message_id, user):

        participants_id_list = await self.delete_message(message_id, user)

        for participant_channel in participants_id_list:

            await participant_channel.send(text_data=json.dumps({
                'type': 'message_deleted',
                'message_id': message_id,
            }))
    


    @database_sync_to_async
    def update_message(self, message_id, user, new_message_content):

        from publish.models import Message

        message = Message.objects.filter(id=message_id).first()

        if message and message.user.id == int(user):

            message.content = new_message_content
            message.save()

            chat = message.room

            participants = chat.users.all()

            participants_id_list = []

            for participant in participants:

                if connected_users.get(participant.id) is not None:

                    participants_id_list.append(connected_users.get(participant.id))

        return participants_id_list

    async def send_update_message(self, message_id, user, new_message_content):

        participants_id_list = await self.update_message(message_id, user, new_message_content)

        for participant_channel in participants_id_list:

            await participant_channel.send(text_data=json.dumps({
                'type': 'message_updated',
                'message_id': message_id,
                'new_content': new_message_content,
            }))
