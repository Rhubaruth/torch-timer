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

    init_duration = models.DurationField(
        blank=False,
        null=False,
        default=timedelta(hours=1),
    )
    effective_duration = models.DurationField(
        blank=False,
        null=False,
        default=timedelta(hours=1),
    )

    effective_end_time = models.DateTimeField(
        blank=False,
        null=False,
        default=timezone.now() + timedelta(hours=1),
    )

    status = models.CharField(
        max_length=12,
        choices=TimerState,
        # choices=[
        #     ("Running", TimerState.RUNNING),
        #     ("Paused", TimerState.PAUSED),
        # ],
        default=TimerState.RUNNING
    )

    def get_duration(self) -> float:
        """ Returns remaining duration of the timer in seconds """
        if self.status == TimerState.RUNNING:
            return (self.effective_end_time - timezone.now()).total_seconds()
        if self.status == TimerState.FINISHED:
            return 0.0
        return self.effective_duration.total_seconds()

    def get_duration_minutes(self, approx: bool = True) -> float:
        duration = self.get_duration()
        if duration < 0:
            return 0
        if approx:
            return floor(duration / (60 * 5)) * 5
        return duration / 60.0

    def terminate_if_finished(self) -> bool:
        # Do nothing for timers with remaining duration
        if self.get_duration() > 0:
            return False

        self.effective_duration = timedelta()
        self.effective_end_time = timezone.now()
        self.status = TimerState.FINISHED

        self.save()
        return True
