import json
from django.utils import timezone
from datetime import timedelta

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Timer, TimerState

from channels.db import database_sync_to_async

from math import floor


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

        # simple authentication
        if not self.scope["user"].is_authenticated \
                or self.scope["user"] != await _get_timer_owner(self.timer_id):
            await self.send(text_data=json.dumps({
                "type": "update.error",
                "msg": "Not Authorised",
            }))
            return

        # Send message to room group
        update = {
            "type": "update.error"
        }
        if "time_delta" in text_data_json:
            # Validate time_delta
            time_delta = text_data_json.get("time_delta")
            if not isinstance(time_delta, (int, float)) \
                    or abs(time_delta) > 3600:
                await self.send(text_data=json.dumps({
                    "type": "update.error",
                    "msg": "Invalid time_delta format.",
                }))
                return

            # Update DB record of the timer
            timer: Timer = await _update_timer_time(
                self.timer_id, delta_sec=time_delta)
            update = {
                "type": "update.time",
                "time_sync": timer.get_duration()
            }
        elif "new_state" in text_data_json:
            # Validate new_state
            new_state = text_data_json.get("new_state")
            if new_state not in ("Running", "Paused"):
                await self.send(text_data=json.dump({
                    "type": "update.error",
                    "msg": "Invalid new_state format.",
                }))
                return

            # Update DB record of the timer
            new_timer: Timer = await _update_timer_state(
                self.timer_id, new_state)
            update = {
                "type": "update.state",
                "new_state": new_timer.state,
                "time_sync": new_timer.get_duration(),
            }

        await self.channel_layer.group_send(
            self.timer_group,
            update
        )

    # Recieve message from room group
    async def update_time(self, event):
        # Send to WebSocket
        await self.send(text_data=json.dumps(event))

    async def update_state(self, event):
        # Send to WebSocket
        await self.send(text_data=json.dumps(event))


@database_sync_to_async
def _get_timer_owner(timer_id):
    timer: Timer = Timer.objects.get(pk=timer_id)
    return timer.created_by


@database_sync_to_async
def _update_timer_time(timer_id: int, delta_sec: float = 0):
    timer: Timer = Timer.objects.get(pk=timer_id)

    timer.duration += timedelta(seconds=delta_sec)

    timer.save()
    return timer


@database_sync_to_async
def _update_timer_state(timer_id: int, new_state):
    timer: Timer = Timer.objects.get(pk=timer_id)

    if new_state == TimerState.RUNNING:
        timer.unpause()
    elif new_state == TimerState.PAUSED:
        timer.pause()

    timer.save()
    return timer
