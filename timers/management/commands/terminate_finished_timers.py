from django.core.management.base import BaseCommand  # , CommandError

from timers.models import Timer, TimerState


class Command(BaseCommand):
    help = 'Terminates all finished timers in DB.'

    def add_arguments(self, parser):
        # parser.add_argument('timer_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        print('TimerTermination')

        timers = Timer.objects.exclude(status=TimerState.FINISHED)
        terminations = [int(t.terminate_if_finished()) for t in timers]

        print(f'Terminated {sum(terminations)}/{len(terminations)} timer(s).')
