from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import TimerForm


def index(request):
    return HttpResponse("Hello, world. You're at the Timers index.")


# @login_required
def timer_add(request):
    canAdd = ''
    
    # timers_count = request.user.timers.all().count()
    #
    # if timers_count >= 5:
    #     canAdd = 'You can\'t have more than 5 timers.'
    #
    # if request.method == 'POST':
    #     form = TimerForm(request.POST)
    #
    #     if form.is_valid():
    #         timer = form.save(commit=False)
    #         timer.created_by = request.user
    #         timer.save()
    #
    #         return redirect('categories')
    # else:

    form = TimerForm()

    context = {
        'form': form,
        'canAdd': canAdd,
    }

    return render(request, 'timers/timer_add.html', context)
