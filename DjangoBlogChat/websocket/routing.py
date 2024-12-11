from django.urls import path
from websocket.consumers import (
    CommunityConsumer,
    ChatConsumer
)

websocket_urlpatterns=[
    path('ws/community', CommunityConsumer.as_asgi()),
    path('ws/chat/<str:chat_name>', ChatConsumer.as_asgi()),

]