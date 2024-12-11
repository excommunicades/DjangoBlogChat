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

        connected_users[self.user_id] = self

        await self.accept()

        for user_id, user in connected_users.items():
            print('User connected:', self.user_id)

            await user.send(text_data=json.dumps({
                'message': f'User connected: {self.user_id}'
            }))

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
