from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

from math import floor


class TimerState(models.TextChoices):
    RUNNING = "Running"
    PAUSED = "Paused"
    FINISHED = "Finished"
    DELETION = "Deletion"


# Create your models here.
class Timer(models.Model):
    created_by = models.ForeignKey(
        User, related_name="timers",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=32, default='')

    start_time = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(
        blank=False,
        null=False,
        default=timedelta(hours=1),
    )

    last_pause_time = models.DateTimeField(null=True, default=None)
    total_paused_time = models.DurationField(
        blank=False,
        null=False,
        default=timedelta(hours=0),
    )

    state = models.CharField(
        max_length=12,
        choices=[
            ("Running", TimerState.RUNNING),
            ("Paused", TimerState.PAUSED),
            ("Finished", TimerState.FINISHED),
        ],
        default=TimerState.RUNNING
    )

    def get_duration(self) -> float:
        """ Returns remaining duration of the timer in seconds """
        if self.state in (TimerState.FINISHED, TimerState.DELETION):
            return 0.0
        now = timezone.now()
        elapsed = now - self.start_time
        duration_seconds = self.duration.seconds
        paused_seconds = self.total_paused_time.seconds

        seconds_left = duration_seconds-elapsed.total_seconds()+paused_seconds
        if self.state == TimerState.RUNNING:
            return max(0, seconds_left)
        return max(0, seconds_left+(now-self.last_pause_time).seconds)

    def get_duration_minutes(self, approx: bool = True) -> float:
        duration = self.get_duration()
        if duration < 0:
            return 0
        if approx:
            return floor(duration / (60 * 5)) * 5
        return duration / 60.0

    def pause(self):
        self.last_pause_time = timezone.now()
        self.state = TimerState.PAUSED
        return

    def unpause(self):
        self.total_paused_time += timezone.now() - self.last_pause_time
        print("TotalPause: ", self.total_paused_time)
        self.last_pause_time = None
        self.state = TimerState.RUNNING
        return

    def terminate_if_finished(self) -> bool:
        # Do nothing for timers with remaining duration
        if self.state in (TimerState.FINISHED, TimerState.DELETION):
            return False
        if self.get_duration() > 0:
            return False

        self.state = TimerState.FINISHED

        self.save()
        return True
