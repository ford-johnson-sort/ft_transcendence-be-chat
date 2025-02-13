# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # The URL route is defined as: /chat/ws/{room_uuid}/{user}
        self.room_uuid = self.scope["url_route"]["kwargs"].get("room_uuid")
        self.username = self.scope["url_route"]["kwargs"].get("user")
        if not self.room_uuid or not self.username:
            await self.close()
            return

        # Try to fetch the room from the DB.
        self.chat_room = await self.get_chat_room(self.room_uuid)
        if not self.chat_room:
            # No such room exists; abort connection.
            await self.close()
            return

        # Ensure that the provided username is one of the room's participants.
        if self.username not in (self.chat_room.user1, self.chat_room.user2):
            await self.close()
            return

        self.room_group_name = f"chat_{self.room_uuid}"

        # Join the channel layer group.
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Optionally, inform the other participant that this user has joined.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_join",
                "message": f"{self.username} has joined the chat.",
            },
        )

    @database_sync_to_async
    def get_chat_room(self, room_uuid):
        try:
            return ChatRoom.objects.get(id=room_uuid)
        except ChatRoom.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        # Inform the group that this user has disconnected.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_leave",
                "message": f"{self.username} has left the chat.",
            },
        )

        # Remove from group.
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # When a message is received, broadcast it to the group.
        data = json.loads(text_data)
        message = data.get("message")
        if not message:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",  # calls chat_message method below
                "message": message,
                "username": self.username,
            },
        )

    async def chat_message(self, event):
        # Forward a chat message to the WebSocket.
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "username": event["username"],
        }))

    async def chat_join(self, event):
        # Inform that a user has joined.
        await self.send(text_data=json.dumps({
            "type": "join",
            "message": event["message"],
        }))

    async def chat_leave(self, event):
        # Inform that a user has left.
        await self.send(text_data=json.dumps({
            "type": "leave",
            "message": event["message"],
        }))
