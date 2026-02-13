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

        # TODO: check message is from authenticated user

        # Send message to room group
        update = {
            "type": "update.error"
        }
        if "time_delta" in text_data_json:
            # Validate time_delta
            time_delta = text_data_json.get("time_delta")
            if not isinstance(time_delta, (int, float)) \
                    or abs(time_delta) > 3600:
                print("Rejected text_data_json because of time_delta.")
                return False
            update = {
                "type": "update.time",
                "time_delta": time_delta,
            }
        elif "new_state" in text_data_json:
            # Validate new_state
            new_state = text_data_json.get("new_state")
            if new_state not in ("Running", "Paused"):
                print("Rejected text_data_json because of new_state.")
                return False
            update = {
                "type": "update.state",
                "new_state": new_state,
            }

        await self.channel_layer.group_send(
            self.timer_group,
            update
        )

    # Recieve message from room group
    async def update_time(self, event):
        # Update DB record of the timer
        _ = await self._update_timer(
            self.timer_id,
            delta_sec=event["time_delta"]
        )

        # Send to WebSocket
        await self.send(text_data=json.dumps(event))

    async def update_state(self, event):
        # Update DB record of the timer
        new_timer = await self._update_timer(
            self.timer_id,
            delta_sec=0,
            state=event["new_state"]
        )

        if event["new_state"] == "Paused":
            event["time_sync"] = new_timer.get_duration()

        # Send to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def _update_timer(self, timer_id: int, delta_sec: float = 0, state=None):
        # Update DB entry
        timer: Timer = Timer.objects.get(pk=timer_id)
        if delta_sec != 0:
            updated_seconds = timer.get_duration() + delta_sec
            timer.effective_duration = timedelta(seconds=int(updated_seconds))
            timer.effective_end_time = timezone.now()+timer.effective_duration
        if state:
            timer.effective_duration = timedelta(
                seconds=int(timer.get_duration()+1)
            )
            timer.effective_end_time = timezone.now()+timer.effective_duration
            timer.status = state
        timer.save()
        return timer
