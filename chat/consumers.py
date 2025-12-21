# chat/consumers.py
import json

# from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_name_group = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_name_group,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name_group,
            self.channel_name
        )

    # Recieve message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_name_group,
            {"type": "chat.message", "message": message}
        )

    # Recieve message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
