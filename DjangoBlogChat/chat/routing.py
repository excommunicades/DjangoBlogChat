from django.urls import re_path
from chat import consumers


websocket_urlpatterns =[
    re_path(r'ws/public_room/$', consumers.PublicConsumer.as_asgi()),

]