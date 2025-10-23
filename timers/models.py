from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class TimerState(models.TextChoices):
    FINISHED = "Finished"
    RUNNING = "Running"
    PAUSED = "Paused"


# Create your models here.
class Timer(models.Model):
    created_by = models.ForeignKey(
        User, related_name="timers",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    init_duration = models.DateTimeField(blank=False, null=False)

    effective_end_time = models.DateTimeField(blank=False, null=False)
    true_end_time = models.DateTimeField(null=True, default=None)

    status = models.IntegerField(
        choices=TimerState,
        default=TimerState.RUNNING
    )

    def get_effective_duration(self):
        duration = self.effective_end_time - datetime()
        # TODO: Check if duration is positive
        return duration
