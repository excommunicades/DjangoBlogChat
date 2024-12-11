import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        pass

    async def disconnect(self):

        pass