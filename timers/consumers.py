import json

from channels.generic.websocket import AsyncWebsocketConsumer


class TimerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.timer_id = self.scope["url_route"]["kwargs"]["timer_id"]
        self.timer_group = f"timer_{self.timer_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.timer_group,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.timer_group,
            self.channel_name
        )

    # Recieve message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # TODO: Update DB entry?

        # Send message to room group
        await self.channel_layer.group_send(
            self.timer_group,
            {"type": "timer.update", "time_delta": message}
        )

    # Recieve message from room group
    async def timer_update(self, event):
        message = event["time_delta"]

        # Send to WebSocket
        await self.send(text_data=json.dumps({"time_delta": message}))
