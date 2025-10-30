from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import TimerForm
from .models import Timer, TimerState


def index(request):
    """ Display all timers that have been not finished. """
    timers = Timer.objects.exclude(status=TimerState.FINISHED)

    context = {
        'timers': timers
    }
    return render(request, 'timers/timers.html', context)


@login_required
def timer_detail(request, timer_id):
    """ Display detail of a timer. """
    timer: Timer = Timer.objects.get(pk=timer_id)

    parts_count = timer.effective_duration.seconds / 720

    context = {
        'timer': timer,
        'parts_count': round(parts_count, 1),
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
            timer.effective_duration = timer.init_duration
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
