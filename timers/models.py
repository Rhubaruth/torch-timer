from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


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
        default=TimerState.RUNNING
    )
