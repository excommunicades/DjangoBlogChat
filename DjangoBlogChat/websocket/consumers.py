from channels.generic.websocket import AsyncWebsocketConsumer
from websocket.websocket_community_action import CommunityAction
import json

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

            await CommunityAction.chat_message(data, self.user_id, connected_users)

        elif action == 'message_status_read':

            messages = data.get('messages').split(',')

            for message_id in messages:

                participants = await CommunityAction.set_status_read(message_id)

                if participants:

                    await participants.send(text_data=json.dumps({
                            'type': 'message_status_read',
                            'message_id': message_id,
                        }))

        elif action == 'get_chat_list':

            result = await CommunityAction.get_chat_list(self.user_id)
            await self.send(text_data=json.dumps(result))

        elif action == 'get_chat_messages':

            chat_id = data.get('chat_id')
            result = await CommunityAction.get_chat_messages(chat_id)

            await self.send(text_data=json.dumps(result))

        elif action == 'delete_chat':

            chat_id = data.get('chat_id')

            participants = await CommunityAction.delete_chat(chat_id, self.user_id)

            if participants:

                for participant_channel in participants:
                    await participant_channel.send(text_data=json.dumps({
                        'type': 'chat_deleted',
                        'chat_id': chat_id,
                    }))

        elif action == 'delete_chat_message':

            message_id = data.get('message_id')
            participants = await CommunityAction.delete_chat_message(message_id, self.user_id)

            for participant_channel in participants:
                await participant_channel.send(text_data=json.dumps({
                    'type': 'message_deleted',
                    'message_id': message_id,
                }))

        elif action == 'update_chat_message':

            message_id = data.get('message_id')
            new_message_content = data.get('new_message_content')
            participants = await CommunityAction.update_chat_message(message_id, self.user_id, new_message_content)

            for participant_channel in participants:
                await participant_channel.send(text_data=json.dumps({
                    'type': 'message_updated',
                    'message_id': message_id,
                    'new_content': new_message_content,
                }))

        elif action == 'forward_message':

            message_content = data.get('message_content')
            from_user_id = data.get('from_user_id')
            from_user_username = data.get('from_user_username')
            to_chat_id = data.get('to_user_id')

            participants = await CommunityAction.forward_chat_message(message_content, from_user_id, to_chat_id)

            for participant_channel in participants:

                await participant_channel.send(text_data=json.dumps({
                    'type': 'forward_message',
                    'message_content': message_content,
                    'from_user_username': from_user_username, 
                }))


    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'user_id': event['user_id'],
            'message': event['message']
        }))
