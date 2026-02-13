import json
from django.utils import timezone
from datetime import timedelta

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Timer

from channels.db import database_sync_to_async


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
        print('recieve ', text_data_json)

        # TODO: check message is from authenticated user

        # Update DB record of the timer
        await self._update_timer(
            self.timer_id,
            float(message)
        )

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

    @database_sync_to_async
    def _update_timer(self, timer_id: int, delta_sec: float):
        print('Updating', timer_id)
        # Update DB entry
        timer: Timer = Timer.objects.get(pk=timer_id)
        updated_seconds = timer.get_duration() + delta_sec
        timer.effective_duration = timedelta(seconds=int(updated_seconds))
        timer.effective_end_time = timezone.now() + timer.effective_duration
        timer.save()
