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
        print('recieve ', text_data_json)

        # TODO: check message is from authenticated user

        # Send message to room group
        update = {
            "type": "update.error"
        }
        if "time_delta" in text_data_json:
            update = {
                "type": "update.time",
                "time_delta": text_data_json["time_delta"],
            }
        elif "new_state" in text_data_json:
            update = {
                "type": "update.state",
                "new_state": text_data_json["new_state"],
            }

        await self.channel_layer.group_send(
            self.timer_group,
            update
        )

    # Recieve message from room group
    async def update_time(self, event):
        # Update DB record of the timer
        new_timer = await self._update_timer(
            self.timer_id,
            delta_sec=event["time_delta"]
        )

        # Send to WebSocket
        await self.send(text_data=json.dumps(event))
        print("update_time ", new_timer)

    async def update_state(self, event):
        # Update DB record of the timer
        new_timer = await self._update_timer(
            self.timer_id,
            delta_sec=0,
            state=event["new_state"]
        )

        print("-----------------------------------")
        print("db state: ", new_timer.status)
        print("db time: ", new_timer.get_duration())
        print("db end: ", new_timer.effective_end_time)

        if event["new_state"] == "Paused":
            event["time_sync"] = new_timer.get_duration()

        # Send to WebSocket
        await self.send(text_data=json.dumps(event))
        print("update_state ", new_timer)

    @database_sync_to_async
    def _update_timer(self, timer_id: int, delta_sec: float = 0, state=None):
        print('Updating', timer_id)
        # Update DB entry
        timer: Timer = Timer.objects.get(pk=timer_id)
        if delta_sec != 0:
            updated_seconds = timer.get_duration() + delta_sec
            timer.effective_duration = timedelta(seconds=int(updated_seconds))
            timer.effective_end_time = timezone.now()+timer.effective_duration
        if state:
            timer.effective_duration = timedelta(
                seconds=int(timer.get_duration())
            )
            timer.effective_end_time = timezone.now()+timer.effective_duration
            timer.status = state
        timer.save()
        return timer
