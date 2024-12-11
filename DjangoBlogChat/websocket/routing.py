from django.urls import path
from websocket.consumers import (
    CommunityConsumer
)

websocket_urlpatterns=[
    path('ws/community', CommunityConsumer.as_asgi()),
    path('ws/chat/<str:chat_name>', CommunityConsumer.as_asgi()),

]