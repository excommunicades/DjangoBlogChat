from django.urls import re_path
from websocket.chat.consumers import (
    PublicConsumer,
    ChatNotificationConsumer,
    ChatConsumer
)


websocket_urlpatterns =[
    re_path(r'ws/public_room$', PublicConsumer.as_asgi()),
    re_path(r'ws/chat/notifications/(?P<user_id>\d+)$', ChatNotificationConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<user1>\w+)/(?P<user2>\w+)/$', ChatConsumer.as_asgi()),

]