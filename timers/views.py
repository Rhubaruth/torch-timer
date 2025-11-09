from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

import json

from .forms import TimerForm
from .models import Timer, TimerState


def index(request):
    """ Display all timers that have been not finished. """
    timers = Timer.objects.exclude(status=TimerState.FINISHED)

    context = {
        'timers': timers
    }
    return render(request, 'timers/timers.html', context)


# @login_required
def timer_detail(request, timer_id):
    """ Display detail of a timer. """
    timer: Timer = Timer.objects.get(pk=timer_id)
    timer.effective_end_time

    print("IsOwner: ", request.user == timer.created_by)

    duration = 0
    if timer.status == TimerState.RUNNING:
        duration = (timer.effective_end_time - timezone.now()).total_seconds()
    elif timer.status == TimerState.PAUSED:
        duration = timer.effective_duration.total_seconds()

    context = {
        'timer': timer,
        'seconds_left': json.dumps(duration)
    }

    return render(request, 'timers/timer_detail.html', context)


@login_required
def timer_add(request):
    canAdd = ''

    if request.method == 'POST':
        form = TimerForm(request.POST)

        if form.is_valid():
            timer: Timer = form.save(commit=False)
            timer.created_by = request.user
            timer.init_duration = timer.effective_duration
            timer.effective_end_time = timezone.now() + timer.init_duration
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
    if request.method == 'POST':
        form = TimerForm(request.POST, instance=timer)

        if form.is_valid():
            form.save()

            timer.effective_end_time = timezone.now() + timer.effective_duration
            timer.save()

            return redirect('timer_detail', timer_id)
    else:
        form = TimerForm(instance=timer)

    context = {
        'form': form,
        'timer': timer
    }

    return render(request, 'timers/timer_edit.html', context)
