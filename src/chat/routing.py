# chat/routing.py
from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'^chat/ws/(?P<room_uuid>[0-9a-f-]+)/(?P<user>\w+)$', ChatConsumer.as_asgi()),
]
