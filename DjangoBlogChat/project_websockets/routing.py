from django.urls import re_path
from project_websockets.chat import consumers as chat
from project_websockets.public import consumers as public

websocket_urlpatterns =[
    re_path(r'ws/public_room$', public.PublicConsumer.as_asgi()),
    re_path(r'ws/chat/notifications/(?P<user_id>\d+)$', chat.ChatNotificationConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<user1>\w+)/(?P<user2>\w+)/$', chat.ChatConsumer.as_asgi()),

]