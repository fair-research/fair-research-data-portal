from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from globus_portal_framework import load_globus_access_token


class Command(BaseCommand):
    help = 'Get a Globus Token for development testing of new services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name', dest='name', required=True,
            help='The Name of the token',
        )

    def handle(self, *args, **options):
        try:
            u = User.objects.filter(username=settings.ME).first()
            name = options['name']
            token = load_globus_access_token(u, name)
            print(token)
        except AttributeError:
            print("Please set username ME = 'person@globusid.org' in "
                  "local_settings.py")
        except ValueError as ve:
            print(ve)
