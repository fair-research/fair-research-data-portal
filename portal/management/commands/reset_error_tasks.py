from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from portal.workflow import TASK_RUNNING, TASK_ERROR
import sys

from portal.models import Task


class Command(BaseCommand):
    help = 'Get a Globus Token for development testing of new services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user', dest='user', required=True,
            help='Which user to use',
        )

        parser.add_argument(
            '--reset', dest='reset', action='store_true',
            help='Reset the tasks to running',
        )


    def handle(self, *args, **options):
        u = User.objects.get(username=options['user'])
        tasks = Task.objects.filter(user=u, status=TASK_ERROR)

        if options.get('reset'):
            for task in tasks:
                task.status = TASK_RUNNING
                task.save()
                task.update()
                print('Updated task, task status now: {} for: {}'.format(
                    task.status,
                    task.input.all().first().description
                ))
                sys.stdout.flush()

        for task in tasks:
            print('Input: {}, Started: {}'.format(
                task.input.all().first().description,
                task.workspace.date_added)
            )
