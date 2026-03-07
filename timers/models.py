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
    created_at = models.DateTimeField(auto_now_add=True)
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
        paused_seconds = self.total_paused_time.total_seconds()

        if self.state == TimerState.PAUSED:
            paused_seconds += (now - self.last_pause_time).total_seconds()

        elapsed = (now - self.start_time).total_seconds() - paused_seconds
        return max(0.0, self.duration.total_seconds() - elapsed)

    def get_duration_minutes(self, approx: bool = True) -> float:
        duration = self.get_duration()
        if approx:
            return floor(duration / (60 * 5)) * 5
        return duration / 60.0

    def pause(self):
        if self.state in (TimerState.FINISHED, TimerState.DELETION):
            return
        self.last_pause_time = self.last_pause_time or timezone.now()
        self.state = TimerState.PAUSED

    def unpause(self):
        if self.state in (TimerState.FINISHED, TimerState.DELETION) \
                or not self.last_pause_time:
            return
        self.total_paused_time += timezone.now() - self.last_pause_time
        self.last_pause_time = None
        self.state = TimerState.RUNNING

    def terminate_if_finished(self) -> bool:
        # Do nothing for timers with remaining duration
        if self.state in (TimerState.FINISHED, TimerState.DELETION):
            return False
        if self.get_duration() > 0:
            return False

        self.state = TimerState.FINISHED

        self.save()
        return True
