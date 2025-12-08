from django.core.management.base import BaseCommand, CommandError
# from timers.models import Timer


class Command(BaseCommand):
    help = 'My test Zdarne command'

    def add_arguments(self, parser):
        print('Zdar ne. add_arguments')
        parser.add_argument('nickname', nargs='+', type=str)

    def handle(self, *args, **options):
        print('Zdar ne. handle')
        print(options)
