from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseForbidden

from datetime import timedelta

import json

from .forms import TimerForm
from .models import Timer, TimerState


def index(request):
    """ Display all timers that have been not queued for deletion. """
    timers = Timer.objects.exclude(state=TimerState.DELETION)

    context = {
        'timers': timers
    }
    return render(request, 'timers/timers.html', context)


def timer_detail(request, timer_id):
    """ Display detail of a timer. """
    timer: Timer = Timer.objects.get(pk=timer_id)

    duration = timer.get_duration()

    context = {
        'timer': timer,
        'seconds_left': json.dumps(duration),
        'timer_active': (timer.state == TimerState.RUNNING
                         or timer.state == TimerState.PAUSED),
    }

    if timer.created_by == request.user:
        return render(request, 'timers/timer_detail_dm.html', context)
    return render(request, 'timers/timer_detail.html', context)


@login_required
def timer_detail_owner(request, timer_id):
    """ Timer view for DM with additional buttons. """
    timer: Timer = Timer.objects.get(pk=timer_id)

    if timer.created_by != request.user:
        return HttpResponseForbidden(
            "You do not have permission for this view."
        )

    duration = timer.get_duration()

    context = {
        'timer': timer,
        'seconds_left': json.dumps(duration),
        'timer_active': (timer.state == TimerState.RUNNING
                         or timer.state == TimerState.PAUSED),
    }

    return render(request, 'timers/timer_detail.html', context)


@login_required
def timer_add(request):
    canAdd = ''

    if request.method == 'POST' and "cancel" not in request.POST:
        form = TimerForm(request.POST)

        if form.is_valid():
            timer: Timer = form.save(commit=False)
            timer.created_by = request.user
            timer.save()

            return redirect('timers')
    else:
        form = TimerForm()

    context = {
        'form': form,
        'canAdd': canAdd,
    }

    return render(request, 'timers/timer_add.html', context)


@login_required
def timer_edit(request, timer_id):
    timer: Timer = Timer.objects.filter(
        created_by=request.user).get(pk=timer_id)
    timer.duration = timedelta(seconds=int(timer.get_duration()))
    timer.save()
    if request.method == 'POST' and "cancel" not in request.POST:
        form = TimerForm(request.POST, instance=timer)

        if form.is_valid():
            form.save()

            if timer.last_pause_time is None \
                    and timer.state == TimerState.PAUSED:
                timer.last_pause_time = timezone.now()
            timer.start_time = timezone.now()
            timer.total_paused_time = timedelta(seconds=0)
            timer.save()

            return redirect('timer_detail', timer_id)
    else:
        form = TimerForm(instance=timer)

    context = {
        'form': form,
        'timer': timer
    }

    return render(request, 'timers/timer_edit.html', context)
