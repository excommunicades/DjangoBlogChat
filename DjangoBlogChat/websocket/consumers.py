import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

connected_users = []
print(connected_users)

class CommunityConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.username = self.scope.get('user', {}).get('username', 'Uknown User')

        connected_users.append(self)

        for user in connected_users:
                if user != self:
                    await user.send(text_data=json.dumps({
                        'message': f'{self.username} connected. Summary connections: {len(connected_users)}'
                    }))
                await user.send(text_data=json.dumps({
                    'message': f'{self.username} connected. Summary connections: {len(connected_users)}'
                }))

        await  self.accept()

    async def disconnect(self):

        connected_users.remove(self)

        for user in connected_users:
            await user.send(text_data=json.dumps({
                'message': f'{self.username} disconnected. Summary connections: {len(connected_users)}'
            }))

    async def receive(self, text_data):

        message = json.loads(text_data).get('message', '')

        for user in connected_users:
            if user != self:
                await user.send(text_data=json.dumps({
                    'message': message
                }))